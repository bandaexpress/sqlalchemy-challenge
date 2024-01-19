# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Stations = Base.classes.station
Measurements = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]"
    )

# Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value. Return the JSON representation of the dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    
    # Extract the date string from the Row object
    most_recent_date_str = most_recent_date[0]
   
    # Convert the string to datetime format
    most_recent_date = dt.datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    
    # Define one_year_ago within the route
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Precipitation data queried for timeframe
    precipitation_data = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= one_year_ago).all()
    
    # Convert the query results to a list of dictionaries
    precipitation_list = [{"date": date, "prcp": prcp} for date, prcp in precipitation_data]

    return jsonify(precipitation_list)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Stations.station).distinct().all()
    stations_list = [station[0] for station in stations_list]
    return jsonify(stations_list)
    
    
# Query the dates and temperature observations of the most-active station for the previous year of data. Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    tobs = session.query(Measurements.date, Measurements.tobs, Measurements.prcp).\
        filter(Measurements.date <= '2016-08-23').\
        filter(Measurements.station == 'USC00519281').\
        order_by(Measurements.date).all()
    
    # Convert the list to Dictionary
    all_tobs = []
    for prcp, date, tobs in tobs:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)


# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.Calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route('/api/v1.0/<start>')
def start_date_summary(start):
    temperature_summary = session.query(func.min(Measurements.tobs).label('min_temp'),
                                        func.avg(Measurements.tobs).label('avg_temp'),
                                        func.max(Measurements.tobs).label('max_temp'))\
        .filter(Measurements.date >= start)\
        .all()
    summary_dict = {
        "Min Temperature": temperature_summary[0].min_temp,
        "Average Temperature": temperature_summary[0].avg_temp,
        "Max Temperature": temperature_summary[0].max_temp
    }
    return jsonify(summary_dict)
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.    
@app.route('/api/v1.0/<start>/<end>')
def start_end_summary(start, end):
    temperature_summary = session.query(func.min(Measurements.tobs).label('min_temp'),
                                        func.avg(Measurements.tobs).label('avg_temp'),
                                        func.max(Measurements.tobs).label('max_temp'))\
        .filter(Measurements.date >= start)\
        .filter(Measurements.date <= end)\
        .all()
    
    summary_dict = {
        "Min Temperature": temperature_summary[0].min_temp,
        "Average Temperature": temperature_summary[0].avg_temp,
        "Max Temperature": temperature_summary[0].max_temp
    }
    return jsonify(summary_dict)


if __name__ == '__main__':
    app.run(debug=True)