import logging
import random
from datetime import datetime, timedelta
from typing import Union

from sqlalchemy import and_, func, desc
from sqlalchemy.exc import IntegrityError

from db import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tracker(db.Model):
    """
    Create Tracker Database Model
    """
    __tablename__ = 'tracker'

    id = db.Column(db.Text, unique=True, primary_key=True, autoincrement=False)
    sub_theme_id = db.Column(db.Integer, db.ForeignKey('subtheme.id'),
                             nullable=False)
    sub_theme = db.relationship("SubTheme")
    description = db.Column(db.Text, nullable=True)
    activated_date = db.Column(db.DateTime, default=datetime.now)
    loc_data = db.relationship("LocationData", back_populates="tracker",
                               primaryjoin="and_(Tracker.id==LocationData.tracker_id)")

    def __init__(self, tracker_id: str, subtheme_id:int, description: str = "",
                 activated_date: datetime.timestamp = datetime.utcnow()) -> None:
        """
        Instantiate Tracker model
        :param tracker_id: New Tracker Id
        :param description: Description of tracker
        :param activated_date: Date Activated
        """
        self.id = tracker_id
        self.sub_theme_id = subtheme_id
        self.activated_date = activated_date
        self.description = description

    @property
    def json_with_location(self) -> dict:
        """
        Get Json encoded Attributes and LocationData
        :return: JSON of the models attributes and associated location data
        """
        return {
            "id": self.id,
            "activated_on": datetime.strftime(self.activated_date, "%d/%m/%y %H:%M"),
            "location_data": [point.json for point in self.loc_data]
        }

    @property
    def json(self) -> dict:
        """
        Get Json encode Attributes
        :return: JSON of the models attributes
        """
        return {
            "id": self.id,
            "activated_on": datetime.strftime(self.activated_date, "%d/%m/%y %H:%M"),
            "description": self.description
        }

    @property
    def kml_coords(self) -> [dict]:
        """
        Create KML (Key Markup Language) Coordinates List
        :return: KML Formatted GPS Coordinates
        """
        return [coord.kml_coord for coord in self.loc_data]

    def save(self) -> None:
        """
        Add Tracker to db session
        """
        try:
            db.session.add(self)
            db.session.flush()
        except IntegrityError as ite:
            db.session.rollback()
            logger.error("Error occurred when saving Tracker to session: id {}".format(self.id),
                         ite.with_traceback(ite.__traceback__))

    def delete(self) -> None:
        """
        Delete Tracker from db session
        """
        try:
            db.session.delete(self)
            db.session.flush()
        except IntegrityError as ite:
            db.session.rollback()
            logger.error("Error occurred when deleting Tracker from session: id {}".format(self.id),
                         ite.with_traceback(ite.__traceback__))

    @staticmethod
    def commit() -> None:
        """ Commit session changes to the database """
        db.session.commit()

    @classmethod
    def get_by_date_range(cls, tracker_id: str, start_date: datetime, end_date: datetime) -> [db.Model]:
        """
        Get Entries between two dates
        :param tracker_id: Tracker Id number
        :param start_date: The date of the oldest data to return
        :param end_date: The date of the newest data to return (inclusive)
        :return: A List of LocationData between the start_date and end_date
        """

        ts_start = datetime.strptime(start_date, '%d/%m/%y')
        ts_end = datetime.strptime(end_date, '%d/%m/%y')

        return cls.query.join(LocationData).filter(cls.id == tracker_id) \
            .filter(and_(LocationData.timestamp >= ts_start, LocationData.timestamp <= ts_end)).all()

    @classmethod
    def get_by_tracker_id(cls, tracker_id: str) -> db.Model:
        """
        Get Tracker by id
        :param tracker_id: Tracker id
        :return: A Tracker with the tracker_id
        """
        return cls.query.filter_by(id=tracker_id).first()

    @classmethod
    def get_by_subtheme_id(cls, subtheme_id: str) -> db.Model:
        """
        Get Tracker by subtheme id
        :param subtheme_id: Subtheme id
        :return: A Tracker with the subtheme_id
        """
        return cls.query.filter_by(sub_theme_id=subtheme_id).all()

    @classmethod
    def get_all(cls) -> db.Model:
        """
        Get all Trackers
        :return: All entries in Tracker table
        """
        return cls.query.all()


class LocationData(db.Model):
    """
    Create Database Model to store location data
    """
    __tablename__ = 'location_data'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    speed = db.Column(db.Float, nullable=True)
    heading = db.Column(db.Float, nullable=True)
    elevation = db.Column(db.Float)
    sat_cnt = db.Column(db.Integer)
    fix_quality = db.Column(db.Integer)
    signal_quality = db.Column(db.Integer)
    battery = db.Column(db.Float, nullable=True)
    charger = db.Column(db.Boolean, nullable=True)
    value = db.Column(db.JSON, default="{}", nullable=True)

    tracker_id = db.Column(db.Text, db.ForeignKey('tracker.id'))
    tracker = db.relationship("Tracker", back_populates="loc_data")

    def __init__(self, tracker_id: str, timestamp: str, longitude: float, latitude: float,
                 speed: float, heading: float, elevation, charger: bool, sat_cnt: int, fix_quality: int,
                 signal_quality: int, battery: float,
                 value: dict = {"o3": str(random.uniform(0, 100)), "no2": str(random.uniform(0, 100))}) -> None:
        """
        Create a instance of LocationData
        :param tracker_id: Tracker Id number
        :param timestamp: When the measurement was taken
        :param longitude: GPS Longitudinal Coordinate in decimal degrees (DD.ddddddd)
        :param latitude: GPS Latitudinal Coordinate in decimal degrees (DD.ddddddd)
        :param speed: Velocity of receiver
        :param heading: Heading (Direction of travel in degrees clockwise from North(0 degrees)
        :param elevation: Height in meters above MSL (Mean Sea Level)
        :param charger: Charging True or False
        :param sat_cnt: GPS Satellite count in use at time of measurement
        :param fix_quality: GPS Fix quality ( 0: not fix, 1: GPS Fix, 2: DGPS, etc...)
        :param signal_quality: RSSI of tracker signal
        :param battery: Battery level in percentage full
        :param value: Value to be stored for location
        """

        self.tracker_id = tracker_id
        if isinstance(timestamp, str):
            self.timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
        else:
            self.timestamp = timestamp
        self.longitude = longitude
        self.latitude = latitude
        self.speed = speed
        self.heading = heading
        self.elevation = elevation
        self.sat_cnt = sat_cnt
        self.fix_quality = fix_quality
        self.signal_quality = signal_quality
        self.battery = battery
        self.charger = charger
        self.value = value

    @staticmethod
    def builder(tracker_id: str = "", timestamp: str = str(datetime.now()), longitude: float = 0.0,
                latitude: float = 0.0,
                speed: float = 0.0, heading: float = 0.0, elevation=0.0, sat_cnt: int = 0, fix_quality: int = 0,
                signal_quality: int = 0,
                battery: float = 0.0, charger: bool = False,
                value: dict = {"o3": str(random.uniform(0, 100)), "no2": str(random.uniform(0, 100))}) -> db.Model:
        """
        Create New LocationData Instance and store in dB. Fill in default values for missing arguments
        :param tracker_id: Tracker Id number
        :param timestamp: When the measurement was taken
        :param longitude: GPS Longitudinal Coordinate in decimal degrees (DD.ddddddd)
        :param latitude: GPS Latitudinal Coordinate in decimal degrees (DD.ddddddd)
        :param speed: Velocity of reciever
        :param heading: Heading (Direction of travel in degrees clockwise from North(0 degrees)
        :param elevation: Height in meters above MSL (Mean Sea Level)
        :param charger: Charging True or False
        :param sat_cnt: GPS Satellite count in use at time of measurement
        :param fix_quality: GPS Fix quality ( 0: not fix, 1: GPS Fix, 2: DGPS, etc...)
        :param signal_quality: RSSI of tracker signal
        :param battery: Battery level in percentage full
        :param value: Value to be stored for location
        :return: A new Instance of LocationData
        """
        return LocationData(tracker_id, timestamp, longitude, latitude, speed, heading, elevation, charger, sat_cnt,
                            fix_quality, signal_quality, battery, value)

    @property
    def json(self) -> dict:
        """
        Get JSON encoded Attributes
        :return:  JSON representation of LocationData instance
        """
        return {"id": self.id,
                "tracker_id": self.tracker_id,
                "timestamp": datetime.strftime(self.timestamp, "%d/%m/%y %H:%M"),
                "coordinates": {"latitude": self.latitude, "logintude": self.longitude, "sat_cnt": self.sat_cnt,
                                "heading": self.heading, "speed": self.speed, "elevation": self.elevation},
                "signal_quality": self.signal_quality,
                "battery": self.battery,
                "charging": self.charger,
                "value": self.value
                }

    @property
    def kml_coord(self) -> (str, str, str):
        """
        Create KML (Key Markup Language) of Coordinate
        :return: KML Formatted GPS Coordinate
        """
        return str(self.latitude), str(self.longitude), str(self.elevation)

    @staticmethod
    def windows_data(tracker_id: Union[str, None] = None, days: int = 365,
                     start_date: datetime = datetime.now()) -> {str: int}:
        """
        Remove data older than X days. Parse a Tracker Id to limit the data deletion to the specified Tracker
        :param start_date: Date of newest data to be kept
        :param tracker_id: Tracker id
        :param days: Number of days old the data must be to be removed
        :return: A JSON response message of the number of entries in the table before, after and the difference after
                 deletion
        """
        rows_before = db.session.query(func.count(LocationData.id)).scalar()

        cut_off_date = start_date - timedelta(days=days)

        if tracker_id:
            LocationData.query.filter(LocationData.timestamp <= cut_off_date).filter(
                LocationData.timestamp > start_date).filter(LocationData.tracker_id == tracker_id).delete()
        else:
            LocationData.query.filter(LocationData.timestamp <= cut_off_date).filter(
                LocationData.timestamp > start_date).delete()

        LocationData.commit()

        rows_after = db.session.query(func.count(LocationData.id)).scalar()
        return dict(before=rows_before, after=rows_after, removed=rows_before - rows_after,
                    code=204 if rows_before - rows_after >= 0 else 500)

    def save(self) -> None:
        """Add LocationData to db Session"""
        try:
            db.session.add(self)
            db.session.flush()
        except IntegrityError as ite:
            db.session.rollback()
            logger.error("Error occurred when saving LocationData to session: id {}".format(self.id),
                         ite.with_traceback(ite.__traceback__))

    def delete(self) -> None:
        """Remove LocationData from db session"""
        try:
            db.session.delete(self)
            db.session.flush()
        except IntegrityError as ite:
            db.session.rollback()
            logger.error("Error occurred when deleting LocationData from session: id {}".format(self.id),
                         ite.with_traceback(ite.__traceback__))

    @staticmethod
    def commit() -> None:
        """ Commit changes to the database """
        db.session.commit()

    @classmethod
    def get_by_date_range(cls, tracker_id: Union[str, None] = None, start_date: datetime = datetime.now(),
                          end_date: datetime = datetime.now()) -> [db.Model]:
        """
        Get Entries by DateTime
        :param tracker_id: Tracker Id Number
        :param start_date: Earliest Date to Fetch entries for
        :param end_date: Latest Date to fetch entries for
        :return: List of LocationData entries
        """
        if end_date < start_date:
            start_date, end_date = end_date, start_date

        end_date += timedelta(days=1.0)

        if not tracker_id:
            return cls.query.filter(and_(cls.timestamp >= start_date, cls.timestamp <= end_date)).all()

        return cls.query.join(Tracker).filter(Tracker.id == tracker_id) \
            .filter(and_(cls.timestamp >= start_date, cls.timestamp <= end_date)).all()

    @classmethod
    def get_by_location(cls, latitude: float, longitude: float, first: bool = True) -> Union[db.Model, list]:
        """
        Fetch database entries by location
        :param latitude: Latitude Decimal Degrees (DD.DDDDD)
        :param longitude: Longitude Decimal Degrees (DD.DDDD)
        :param first: If True only the first matching db entry is returned otherwise all matching db entries
               are returned
        :return: Entries or first entry in database with the matching coordinates
        """
        if first:
            return cls.query.filter_by(latitude=latitude, longitude=longitude).first()
        else:
            return cls.query.filter_by(latitude=latitude, longitude=longitude)

    @classmethod
    def get_by_tracker_id(cls, tracker_id: str, first: bool = True) -> Union[db.Model, list]:
        """
        Get Entry / Entries by Tracker id
        :param tracker_id: Tracker id
        :param first: If True only the first entry found is returned, otherwise all found entries are returned
        :return: Entry or Entries related to the Tracker Id parsed
        """
        if first:
            return cls.query.filter_by(tracker_id=tracker_id).first()
        else:
            return cls.query.filter_by(tracker_id=tracker_id)

    @classmethod
    def get_by_tracker_id_with_limit(cls, tracker_id: str,
                                     limit: int) -> Union[db.Model, list]:
        """
        Get limit number of entries which contain the corresponding tracker_id
        :param tracker_id: Tracker id.
        :param limit: number of entries to return.
        :return: Entries related to the Tracker Id passed.
        """
        return cls.query.filter_by(tracker_id=tracker_id).order_by(desc(
            LocationData.timestamp)).limit(limit)

    @classmethod
    def get_by_id(cls, loc_id: str) -> db.Model:
        """
        Get LocationData by id
        :param loc_id: LocationData id
        :return: LocationData entry
        """
        return cls.query.filter_by(id=loc_id).first()

    @classmethod
    def get_tracker_attributes(cls, tracker_id: str) -> Union[list, None]:
        """
        Get the attributes a tracker records
        :param tracker_id: A tracker id
        :return: The attributes a tracker senses
        """
        tracker = cls.query.filter_by(tracker_id=tracker_id).first()
        if tracker:
            tracker_dict = dict(tracker.value)
            return [*tracker_dict]
        else:
            return None

    @classmethod
    def does_tracker_record(cls, tracker_id: str, attr: str) -> Union[bool,
                                                               None]:
        """
        Get the attributes a tracker records
        :param tracker_id: A tracker id
        :return: The attributes a tracker senses
        """
        tracker = cls.query.filter_by(tracker_id=tracker_id).first()
        if tracker:
            tracker_dict = dict(tracker.value)
            if attr in [*tracker_dict]:
                return True
            else:
                return False
        else:
            return None
