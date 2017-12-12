from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, String, Date, Time, DateTime

Base = declarative_base()

class Agency(Base):
    __tablename__ = "agencies"

    agency_id = Column(String(64), primary_key=True)
    agency_name = Column(String(64))
    agency_url = Column(String(64))
    agency_timezone = Column(String(64))
    agency_lang = Column(String(64))
    agency_phone = Column(String(64))
    agency_fare_url = Column(String(64))

class Calendar(Base):
    __tablename__ = "calendars"

    service_id = Column(String(64), primary_key=True)
    monday = Column(Integer)
    tuesday = Column(Integer)
    wednesday = Column(Integer)
    thursday = Column(Integer)
    friday = Column(Integer)
    saturday = Column(Integer)
    sunday = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

class CalendarDate(Base):
    __tablename__ = "calendar_dates"

    service_id = Column(String(64), primary_key=True)
    date = Column(Date)
    exception_type = Column(Integer)

class Route(Base):
    __tablename__ = "routes"

    route_id = Column(String(64), primary_key=True)
    agency_id = Column(String(64), index=True)
    route_short_name = Column(String(64))
    route_long_name = Column(String(64))
    route_desc = Column(String(64))
    route_type = Column(String(64))
    route_url = Column(String(64))
    route_color = Column(String(64))

class Shape(Base):
    __tablename__ = "shapes"

    shape_id = Column(String(64), primary_key=True)
    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_pt_sequence = Column(Integer)

class Stop(Base):
    __tablename__ = "stops"

    stop_id = Column(String(64), primary_key=True)
    stop_code = Column(Integer)
    stop_name = Column(String(64))
    stop_desc = Column(String(64))
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    zone_id = Column(String(64))

class StopTime(Base):
    __tablename__ = "stop_times"

    id = Column(Integer, primary_key=True)
    trip_id = Column(String(64), index=True)
    arrival_time = Column(Time)
    departure_time = Column(Time)
    stop_id = Column(String(64), index=True)
    stop_sequence = Column(Integer)
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)


class Transfer(Base):
    __tablename__ = "transfers"

    from_stop_id = Column(String(64), primary_key=True)
    to_stop_id = Column(String(64), primary_key=True)
    transfer_type = Column(Integer)


class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(String(64), primary_key=True)
    route_id = Column(String(64), index=True)
    service_id = Column(String(64), index=True)
    trip_headsign = Column(String(128))
    direction_id = Column(String(64))
    block_id = Column(String(64))
    shape_id = Column(String(64), index=True)


class ApcAvlRecord(Base):
    __tablename__ = 'apc_avl_records'

    id = Column(Integer, primary_key=True)
    day_of_week = Column(Integer)
    direction = Column(Integer)
    route = Column(String(64), index=True)
    trip = Column(String(64))  # not compatible ids
    block = Column(String(64), index=True)  # needs hyphen
    stop = Column(Integer, index=True)
    vehicle_id = Column(Integer)
    arrival_time = Column(DateTime)
    departure_time = Column(DateTime)
    boarding = Column(Integer)
    alighting = Column(Integer)
    load = Column(Integer)
    scheduled_arrival = Column(DateTime)
    predicted_travel_time = Column(Float)
    actual_travel_time = Column(Float)