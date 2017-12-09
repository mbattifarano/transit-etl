from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKey, Float, Integer, String, Date, Time
from sqlalchemy.orm import relationship

Base = declarative_base()

class Agency(Base):
    __tablename__ = "agencies"

    agency_id = Column(Integer, primary_key=True)
    agency_name = Column(String)
    agency_url = Column(String)
    agency_timezone = Column(String)
    agency_lang = Column(String)
    agency_phone = Column(String)
    agency_fare_url = Column(String)

class Calendar(Base):
    __tablename__ = "calendars"

    service_id = Column(String, primary_key=True)
    monday = Column(Integer)
    tuesday = Column(Integer)
    wednesday = Column(Integer)
    thursday = Column(Integer)
    friday = Column(Integer)
    saturday = Column(Integer)
    sunday = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

    exception = relationship("CalendarDate", primaryjoin="service_id==calendar_dates.service_id")

class CalendarDate(Base):
    __tablename__ = "calendar_dates"

    service_id = Column(String, primary_key=True)
    date = Column(Date)
    exception_type = Column(Integer)

class Route(Base):
    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True)
    agency_id = Column(Integer, ForeignKey(Agency.agency_id), index=True)
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_desc = Column(String)
    route_type = Column(String)
    route_url = Column(String)

    agency = relationship(Agency, backref="routes")

class Shape(Base):
    __tablename__ = "shapes"

    shape_id = Column(Integer, primary_key=True)
    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_pt_sequence = Column(Integer)

class Stop(Base):
    __tablename__ = "stops"

    stop_id = Column(String, primary_key=True)
    stop_code = Column(Integer)
    stop_name = Column(String)
    stop_desc = Column(String)
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    zone_id = Column(String)

    transfers = relationship("Stop", secondary="Transfer",
                             primaryjoin="id == transfers.from_stop_id",
                             secondaryjoin="id == transfers.to_stop_id")

class StopTime(Base):
    __tablename__ = "stop_times"

    id = Column(Integer, primary_key=True)
    trip_id = Column(String, ForeignKey("trips.trip_id"), index=True)
    arrival_time = Column(Time)
    departure_time = Column(Time)
    stop_id = Column(String, ForeignKey(Stop.stop_id), index=True)
    stop_sequence = Column(Integer)
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)

    trip = relationship("Trip", backref="stop_times")
    stop = relationship(Stop, backref="stop_times")

class Transfer(Base):
    __tablename__ = "transfers"

    from_stop_id = Column(String, ForeignKey(Stop.stop_id), primary_key=True)
    to_stop_id = Column(String, ForeignKey(Stop.stop_id), primary_key=True)
    transfer_type = Column(Integer)


class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(String, primary_key=True)
    route_id = Column(String, ForeignKey(Route.route_id), index=True)
    service_id = Column(String, ForeignKey(Calendar.service_id), index=True)
    trip_headsign = Column(String)
    direction_id = Column(String)
    block_id = Column(String)
    shape_id = Column(String, ForeignKey(Shape.shape_id), index=True)