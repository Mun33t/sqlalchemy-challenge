# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import datetime as dt


#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect = True)

# Save the references fore each table
Measurement = Base.classes.meeasurement
Station = Base.classes.station


#Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)

#################################################

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Precipitation route
@app.route("/api/v.1.0/precipitation")
def precipitation():
    session = Session()
   # Data for last 12 months
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year = dt. datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    # Data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    # Dictionary (date as key, precipitation as value)
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    # Close Session 
    session.close
    return jsonify(precipitation_dict)

# Stations route
@app.route("/api.v1.0/stations")
def stations():
    session = Session()
    stations_data = session.query(Station.station).all()
    stations_list = [station[0] for station in stations_data]

    session.close()
    return jsonify(stations_list)

# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session()
    # Most Active Station Data (last 12 months)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    # Json list of last year's temp observations
    most_active_station_id = session.query(Measurement.station).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    temperature_data = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= last_year).all()
    temperature_list = [temp[0] for temp in temperature_data]
    # Close Session
    session.close()
    return jsonify(temperature_list)

# Statistics route for start date
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session()
    # JSON list for min, avg, and max temp of specified date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    # Create a dict that holds the results
    stats = {
        "tmin": results[0][0],
        "tavg": results[0][1],
        "tmax": results[0][2]
    }
    # Close session
    session.close() 
    return jsonify(stats)   

# Stats route for start and end date 
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session()
    # JSON list for min, avg, and max temp of specified date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Create a dictionary for the results
    stats = {
        "tmin": results[0][0],
        "tavg": results[0][1],
        "tmax": results[0][2]
    }
    # Close session
    session.close()
    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True)