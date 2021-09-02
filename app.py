import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, json, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# print(Base.classes.keys())
# Save reference to the table
Measurement = Base.classes.measurement
Stations = Base.classes.station

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
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start_date</br>"
        f"/api/v1.0/start_date/end_date</br>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    #Create a session from python to db
    session = Session(engine)

    """Return a list of Precipitation Data"""
    # Query all precipitation
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-24").\
        all()

    session.close()

    # Convert list to a dictionary
    all_prcp = []
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp

        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():

    # Create session to link from Python to db
    session = Session(engine)

    stations = []

    

    """Return a list of all Stations"""
    # Query all stations
    station_results = session.query(Station.station, Station.name).all()
    
    session.close() 

    return jsonify(station_results)


    # # Convert list of tuples
    # all_stations = list(np.ravel(results))


@app.route("/api/v1.0/tobs")
def tobs():
    # Create session to link Python to db
    session = Session(engine)

    #Query the dates and temperature observations of the most active station for the last year of data.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year_date = (dt.datetime.strptime(last_date[0], '%Y-%m-%d') /
    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    temp_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_year_date).\
        order_by(Measurement.date).all()

    session.close()

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_list = []

    for date, tobs, in temp_results:
        new_dict = {}
        new_dict["date"] = tobs
        tobs_list.append(new_dict)

        return jsonify(tobs_list)


@app.route("/api/v1.0/start_date")
def Start_date(start_date):
    # Create a session link from Python to db
    session = Session(engine)

    """Return a list of min, avg and max tobs for a start date"""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    #Create a dictionary from the row data and append to a list of start_date_tobs
    start_date_tobs = []
    for min, avg, max, in results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min_temp"] = min
        start_date_tobs_dict["avg_temp"] = avg
        start_date_tobs_dict["max_temp"] = max
        start_date_tobs.append(start_date_tobs_dict)

        return jsonify(start_date_tobs)
    
@app.route("/api/v1.0/start_date/end_date")
def Start_end_date(start_date, end_date):

    # Create our session from Python to db
    session = Session(engine)

    """Return a list of min, avg, max tobs for stat and end dates"""

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >=start_date).filter(Measurement.date <= end_date).all()

    session.close()

    #Create a dictionary from the row dataand append to a list of start_end_tobs
    start_end_tobs = []
    for min, avg, max in results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["min_temp"] = min
        start_end_tobs_dict["avg_temp"] = avg 
        start_end_tobs_dict["max_temp"] = max
        start_end_tobs.append(start_end_tobs_dict)

    return jsonify(start_end_tobs)

if __name__ == "__main__":
    app.run(debug=True)