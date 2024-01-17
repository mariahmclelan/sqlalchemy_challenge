# Import the dependencies.
import numpy as np
import flask 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc, text
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= one_year_ago)\
    .order_by(Measurement.date).all()
    session.close()

    # Dictonary of the precipitation data
    precipitation = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query list of stations
    stations = session.query(Station.station).all()
    session.close()

    # List of stations
    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Querey dates and temperatures from the most active stations past 12 months
    temperature_data = session.query(Measurement.tobs)\
    .filter(Measurement.station == 'USC00519281')\
    .filter(Measurement.date >= one_year_ago)\
    .order_by(Measurement.date).all()
    session.close()

    # List of temp observations
    all_temperature = list(np.ravel(temperature_data))
    return jsonify(all_temperature)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dates(start=None, end=None):
    session = Session(engine)

    # Query min,max,avg for temp for specified date
    sel = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)
       ]
    if not end: 
        active_station_info = session.query(*sel).filter(Measurement.date >= start).all()

        session.close()
        all_date = list(np.ravel(active_station_info))
        return jsonify(all_date)
    
    active_station_info = session.query(*sel).filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()
    session.close()

    # List min, max, avg for specidied dates
    all_date = list(np.ravel(active_station_info))
    return jsonify(all_date)


if __name__ == '__main__':
    app.run()