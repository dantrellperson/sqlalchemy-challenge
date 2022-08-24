# Dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# automap sqlite database file
Base = automap_base()

# reflect database
Base.prepare(engine, reflect=True)

# variables for each table
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

# flask

app = Flask(__name__)

# define welcome route


@app.route('/')
def welcome():
    """Welcome to the Hawaii weather API!"""
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/temp/start/end"
        f"PLEASE READ: Start and end date require format: YYYY-mm-dd/YYYY-mm-dd"
    )

# define precipitation route


@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)

    # Variable for results
    pResults = session.query(measurement.prcp, measurement.date).all()

    # Close session
    session.close()

    values = []
    for prcp, date in pResults:
        dict1 = {}
        dict1["precipitation"] = prcp
        dict1["date"] = date
        values.append(dict1)

    return jsonify(values)


# define stations route


@app.route('/api/v1.0/stations')
def stations():

    results = session.query(station.station).all()

    session.close()

    allStations = list(np.ravel(results))

    return jsonify(allStations)

# define temperature route


@app.route('/api/v1.0/tobs')
def tobs():

    stationTotal = session.query(station.name).count()

    activeStation = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()

    queryDate = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= queryDate).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps)

# Return a JSON list of the min, max, and avg temperature, for  given range.


@app.route("/api/v1.0/<date>")
def startDateOnly(date):

    # get results
    session = Session(engine)

    dayTempResults = session.query(func.min(measurement.tobs), func.avg(measurement.tobs),
                                   func.max(measurement.tobs)).filter(measurement.date >= date).all()
    session.close()

    values = []
    # for loop to show on app
    for min, avg, max in dayTempResults:
        dict1 = {}
        dict1["min"] = min
        dict1["average"] = avg
        dict1["max"] = max
        values.append(dict1)

    return jsonify(values)


# Return a JSON list of the min, max, and avg temperature, for  given range.
@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start, end):
    session = Session(engine)

    multiDayResults = session.query(func.min(measurement.tobs), func.avg(measurement.tobs),
                                    func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    values = []
    # for loop to show on app
    for min, avg, max in multiDayResults:
        dict1 = {}
        dict1["min"] = min
        dict1["average"] = avg
        dict1["max"] = max
        values.append(dict1)

    return jsonify(values)


if __name__ == "__main__":
    app.run(debug=True)
