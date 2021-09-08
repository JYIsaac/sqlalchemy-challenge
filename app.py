import numpy as np

import datetime as dt

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
Station = Base.classes.station

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
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation</br>"
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
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year_date = dt.date(2017,8,23) - dt.timedelta(days=365)



    query_results = session.query(Measurement.tobs,Measurement.date ).\
    filter(Measurement.date >=last_year_date).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date <=recent_date).\
         order_by(Measurement.date).all()
    
    session.close()
    # Create a dictionary from the row data and append to a list of all precipitation 
    all_tobs = []
    for row in query_results:
       tobs_dict = {}
       tobs_dict["tobs"] = row.tobs
       tobs_dict["Date"] = row.date
       all_tobs.append(tobs_dict)
 
    return jsonify(all_tobs)



@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_start_end_date(start_date,end_date):
    session = Session(engine)
    min_max_avg_temp=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
    func.avg(Measurement.tobs))\
    .filter(Measurement.date >= start_date)\
    .filter(Measurement.date <= end_date).all()


    sd = [func.min(Measurement.tobs),
     func.max(Measurement.tobs),
     func.avg(Measurement.tobs)]

    if not end_date:
        min_max_avg_temp=session.query(*sd)\
        .filter(Measurement.date >= start_date).all()

        temps = list(np.ravel(min_max_avg_temp))


    else:
        min_max_avg_temp=session.query(*sd)\
        .filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

        temps = list(np.ravel(min_max_avg_temp))

    temps.append(start_date)
    session.close()

    # all_tobs_data_user_date_range = []
    # for row in min_max_avg_temp:
    #    tobs_temp_date_range_dict = {}
    #    tobs_temp_date_range_dict["min_tobs"] = row[0]
    #    tobs_temp_date_range_dict["max_tobs"] = row[1]
    #    tobs_temp_date_range_dict["avg_tobs"] = row[2]
    #    all_tobs_data_user_date_range.append(tobs_temp_date_range_dict)

    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug=True)