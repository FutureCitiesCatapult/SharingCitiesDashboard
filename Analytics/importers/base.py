import json
import logging
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Any, Callable, Union

import pandas as pd
import requests
import sqlalchemy
from geoalchemy2.elements import WKTElement
from requests import HTTPError
from sqlalchemy.exc import IntegrityError

from db import db
from importers.json_reader import JsonReader
from models import location
from models.api import API
from models.attribute_data import ModelClass
from models.attributes import Attributes
from models.sensor import Sensor
from models.sensor_attribute import SensorAttribute
from models.theme import Theme, SubTheme
from models.unit import Unit
from utility import convert_unix_to_timestamp, convert_to_date
from .state_decorator import ImporterStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseImporter(object):
    importer_status = ImporterStatus.get_importer_status()

    def __init__(self, api_name: str, url: str, refresh_time: int, api_key: str, api_class: Callable,
                 token_expiry: datetime) -> None:
        """
        Base Importer
        All the importers needs to be extended from this class
        The class provides methods to save API, Sensor, Attributes, Location and Data Tables
        All the methods provided here can be overridden or can be extended by calling the super method
        from base class and then extending it in Child class
        All new common functionality can be added to this base class, which then automatically be inherited
        by all the child classes.
        :param api_name: The name of the API, it needs to be unique, else database waring would be received
        :param url: he url which needs to be pinged to get the data, periodically
        :param refresh_time: After how many seconds the API needs to be pinged
        :param api_key: Key to access the API (if any)
        :param api_class: The full path of the class from package to class name like importers.air_quality.KCLAirQuality
        :param token_expiry: Time in which token will get expired, so that new token can be renewed again
        """
        self.api_name = api_name
        self.url = url
        self.refresh_time = refresh_time
        self.api_key = api_key
        self.token_expiry = token_expiry
        self.api_class = api_class
        self.dataset = None

    def _create_datasource(self, headers: Union[dict, str]) -> None:
        """
        Create DataSource
        :param headers: Request headers
        :return: None
        """
        _, status_code, message = self.load_dataset(headers)

        if status_code == 498 or status_code == 499:
            self._refresh_token()

        if status_code != 200:
            raise HTTPError(message)
        return

    def _refresh_token(self):
        """
        Refresh token must be overriden by sub class
        :param args: Additional arguments
        :raises: NotImplementedError when not overriden by class
        """
        raise NotImplementedError

    def load_dataset(self, headers: str) -> (Any, HTTPStatus):
        """
        Load Data set
        :param headers: Request headers
        :return: Data set and an HTTP status code
        """
        data = requests.get(self.url.replace(' ', '').replace('\n', '') + self.api_key, headers=headers)

        self.dataset = json.loads(data.text)
        status_code, message = self.nginx_http_status(self.dataset, data.status_code)
        return self.dataset, status_code, message

    def nginx_http_status(self, data: dict, status_code: int) -> (int, Union[str, None]):
        """
        Handle nginx status code in content body.
        :param data: HTTP response data
        :param status_code: HTTP status code
        :return: NGINX response status
        """
        message: str = None

        if isinstance(data, dict):

            try:
                status = int(data['error']['code'])
                if 'message' in data['error']:
                    message = data['error']['message']
                return status, message
            except Exception:
                return status_code, None

        return status_code, None

    def create_dataframe(self, object_separator: Union[str, None] = None, ignore_tags: [str] = [],
                         ignore_values: [Any] = [],
                         ignore_tag_values: {str: Any} = {}, ignore_object_tags: [str] = []) -> pd.DataFrame:
        """
        Create Pandas DataFrame
        :param object_separator: Token to tokenize entries
        :param ignore_tags: tags to be ignored
        :param ignore_values: Values to ignore
        :param ignore_tag_values: Values of tags to be ignored
        :param ignore_object_tags: Object tags to be ignored
        :return: Pandas Data Frame
        """
        jr = JsonReader(object_seperator=object_separator)

        jr.create_objects(self.dataset, ignore_tags=ignore_tags, ignore_values=ignore_values,
                          ignore_tag_values=ignore_tag_values, ignore_object_tags=ignore_object_tags)
        df = jr.create_dataframe()

        return df

    def create_datasource(self, dataframe: pd.DataFrame, sensor_tag: str, attribute_tag: [str],
                          unit_value: [str], description: [str], bespoke_unit_tag: [str],
                          bespoke_sub_theme: [str], location_tag: location.Location,
                          sensor_prefix: Union[str, None] = None,
                          api_timestamp_tag: Union[str, None] = None, check_sensor_exists_by_name: bool = False,
                          check_sensor_exists_by_name_loc: bool = False,
                          check_sensor_exists_by_name_api: bool = False, is_dependent: bool = False) -> None:
        """
        Setup the database for the new Importer/API
        :param dataframe: pandas dataframe
        :param sensor_tag: Takes a column name from the DataFrame whose value would act as sensor
        :param attribute_tag: Takes a list of column names from the DataFrame
        :param unit_value:  Takes a list of column names from DataFrame which would act as unit value
                            for an attribute and they need to be passed in the same order as attribute
                            e.g
                            passing an attribute list as ['no2', 'rainfall'] which are 2 separate cols in dataframe
                            and if their unit values are contained in two separate cols in dataframe like
                            ['no2_unit', 'rainfall_unit'], then these two unit col names should come in the same
                            order, if only one col name is provided for 2 attributes then that one unit value col
                            would be assigned both attributes.
                            If you want to assign the unit value to one col e.g for 2 attributes
                            ['no2', 'rainfall'], you have only one unit value col ['no2_unit'] and dont want
                            it to get assigned to rainfall attribute then pass the unit_value as
                            ['no2_unit', None]
        :param description: description
        :param bespoke_unit_tag: Accepts a list and follows the same principle as unit_value, unit tag is usually
                                 something like a unit that a value is expressed in like kg but this has to exists in
                                 our database.
        :param bespoke_sub_theme: Subtheme
        :param location_tag: Takes an object of Location class which in turn contains the name of the latitude and
                             longitude cols.
        :param sensor_prefix: Prefix for all the sensor tags
        :param api_timestamp_tag:
        :param check_sensor_exists_by_name: Check if sensor exists
        :param check_sensor_exists_by_name_loc: check if location and name exsist
        :param check_sensor_exists_by_name_api: check api exists by name
        :param is_dependent: Is independant
        """
        api_id = self.stage_api_commit()
        # Location tag
        latitude, longitude = None, None

        if location_tag is not None:
            latitude = dataframe[location_tag.lat].tolist()
            longitude = dataframe[location_tag.lon].tolist()

        # Save location and sensor
        sensor_objects = self.save_sensors(dataframe[sensor_tag].tolist(), latitude, longitude, api_id,
                                           sensor_prefix,
                                           check_sensor_exists_by_name=check_sensor_exists_by_name,
                                           check_sensor_exists_by_name_loc=check_sensor_exists_by_name_loc,
                                           check_sensor_exists_by_name_api=check_sensor_exists_by_name_api,
                                           is_dependent=is_dependent)

        # Save Attributes
        attr_objects = self.save_attributes(attribute_tag, unit_value, description,
                                            bespoke_unit_tag, bespoke_sub_theme)

        # Save attribute and sensor relation
        self.save_attr_sensor(attr_objects, sensor_objects.values())
        self.create_tables(attr_objects)
        self.insert_data(attr_objects, sensor_objects, dataframe, sensor_tag, sensor_prefix, api_timestamp_tag)

    '''
    
    '''

    def create_datasource_with_values(self, dataframe: pd.DataFrame, sensor_tag: str, attribute_tag: str,
                                      value_tag: str,
                                      latitude_tag: str, longitude_tag: str, description_tag: str,
                                      api_timestamp_tag: Union[str, None] = None,
                                      unit_tag: Union[str, None] = None, unit_value_tag: Union[str, None] = None,
                                      unit_id: int = 1, unit_value: int = 1, sub_theme: int = 1) -> None:
        """
        Setup the database for the new Importer/API and commit Values.
        Consider values of the tags as sensors, attributes and data values instead of the tags themselves

        ========================
        |   A   |   B    |  C  |
        |----------------------|
        |   BG1 |   NO2  |  22 |
        |   BG2 |   SO2  |  23 |
        ========================

        Column A: Site Code
        Column B: Attributes
        Column C: Values


        :param dataframe: Pandas Dataframe to save
        :param sensor_tag: sensor tag
        :param attribute_tag:
        :param value_tag: value tag
        :param latitude_tag: latitude tag
        :param longitude_tag: longitude tag
        :param description_tag: description tag
        :param api_timestamp_tag: timestamp tag
        :param unit_tag: unit tag
        :param unit_value_tag: Unit value tag
        :param unit_id: Unit Id
        :param unit_value: unit value
        :param sub_theme: SubTheme Id
        """

        api_id = self.stage_api_commit()
        _unit = None
        _unit_value = None

        sensors = dataframe[sensor_tag].tolist()
        attributes = dataframe[attribute_tag].tolist()
        latitude = dataframe[latitude_tag].tolist()
        longitude = dataframe[longitude_tag].tolist()
        description = dataframe[description_tag].tolist()

        if unit_tag is None:
            _unit = unit_id
        else:
            _unit = dataframe[unit_tag].tolist()

        if unit_value_tag is None:
            _unit_value = unit_value
        else:
            _unit_value = dataframe[unit_value_tag].tolist()

        sensor_objects = self.save_sensors(sensors, latitude, longitude, api_id, None,
                                           check_sensor_exists_by_name=False,
                                           check_sensor_exists_by_name_loc=False,
                                           check_sensor_exists_by_name_api=False)

        attr_objects = self.save_attributes(attributes,
                                            _unit_value if isinstance(_unit_value, list) else [_unit_value],
                                            description,
                                            _unit if isinstance(_unit, list) else [_unit],
                                            [sub_theme])
        self.save_attr_sensor(attr_objects, sensor_objects.values())
        self.create_tables(attr_objects)
        self.insert_data(attr_objects, sensor_objects, dataframe, sensor_tag, '',
                         api_timestamp_tag, value_tag, attribute_tag, unit_value_tag)

    def save_sensors(self, sensors: list, latitude: list, longitude: list, api_id: int, sensor_prefix: str,
                     **kwargs: {str: Any}) -> [db.Model]:
        """
        Save Sensor Values
        :param sensors: Sensors
        :param latitude: list of latitudes for sensors
        :param longitude: list of longitudes for sensors
        :param api_id: api id
        :param sensor_prefix: sensors prefix
        :param kwargs: keyword arguments
        :return: returns a list of sensors
        """
        sensor_objects = {}
        sensor_exists = set()

        for i in range(len(sensors)):
            # if sensor already exists dont save
            if kwargs['check_sensor_exists_by_name']:
                s_name = sensor_prefix + str(sensors[i]) if sensor_prefix is not None else str(sensors[i])
                _sensor = Sensor.get_by_name(s_name)
                if _sensor:
                    sensor_objects[_sensor.name] = _sensor
                    continue

            if kwargs['check_sensor_exists_by_name_loc']:
                s_name = sensor_prefix + str(sensors[i]) if sensor_prefix is not None else str(sensors[i])
                _sensor = Sensor.get_by_name_loc(s_name, None)  # This needs to be fixed
                if _sensor:
                    sensor_objects[_sensor.name] = _sensor
                    continue

            if kwargs['check_sensor_exists_by_name_api']:
                s_name = sensor_prefix + str(sensors[i]) if sensor_prefix is not None else str(sensors[i])
                _sensor = Sensor.get_by_name_api(s_name, api_id)
                if _sensor:
                    sensor_objects[_sensor.name] = _sensor
                    continue

            loc = self.save_location(float(latitude[i]), float(longitude[i]))

            s_name = sensor_prefix + str(sensors[i]) if sensor_prefix is not None else str(sensors[i])
            _hash = self._hash_it(str(api_id), str(loc.id), s_name)
            if _hash in sensor_exists:
                continue

            if 'is_dependent' in kwargs:
                if kwargs['is_dependent']:
                    _sensor = Sensor._get_by_api_location_name(a_id=api_id, l_id=loc.id, name=s_name)
                    if _sensor:
                        sensor_objects[_sensor.name] = _sensor
                        sensor_exists.add(_hash)
                        logger.info('{} sensor already exists with API ID: {} and Location ID:'.format(s_name,
                                                                                                       str(api_id),
                                                                                                       str(loc.id)))
                        continue

            sensor = Sensor(str(uuid.uuid4()), api_id, loc.id, s_name)
            sensor_exists.add(_hash)

            sensor = sensor.save()
            sensor_objects[sensor.name] = sensor

        return sensor_objects

    def save_location(self, latitude: float, longitude: float) -> db.Model:
        """
        Save location data
        :param latitude: GPS Latitude
        :param longitude: Gps Longitude
        :return: The location
        """
        loc = location.Location.get_by_lat_lon(latitude, longitude)
        if not loc:
            loc = location.Location(latitude, longitude, WKTElement('POINT(%f %f)' % (latitude, longitude), 4326))
            loc.save()

        return loc

    def save_attributes(self, attribute_tag: list, unit_value: list, description: list,
                        bespoke_unit_tag: list, bespoke_sub_theme: list) -> [db.Model]:
        """
        Save attributes
        :param attribute_tag: Attribute tags
        :param unit_value: Unit values
        :param description: Attribute descriptions
        :param bespoke_unit_tag: unit
        :param bespoke_sub_theme: Parent subtheme name
        :return: A list of Attributes
        """
        attr_objects = []
        attr_exists = set()
        for i in range(len(attribute_tag)):
            uv = None
            but = None
            bst = None
            des = None
            if len(unit_value) == len(attribute_tag):
                uv = unit_value[i]
            else:
                if len(unit_value) > 0:
                    uv = unit_value[0]

            if len(description) == len(attribute_tag):
                des = description[i]
            else:
                if len(description) > 0:
                    des = description[0]

            if len(bespoke_unit_tag) == len(attribute_tag):
                but = bespoke_unit_tag[i]
            else:
                if len(bespoke_unit_tag) > 0:
                    but = bespoke_unit_tag[0]

            if len(bespoke_sub_theme) == len(attribute_tag):
                bst = bespoke_sub_theme[i]
            else:
                if len(bespoke_sub_theme) > 0:
                    bst = bespoke_sub_theme[0]

            _hash = self._hash_it(str(attribute_tag[i]), str(but), str(uv))
            if _hash in attr_exists:
                continue

            a = self.stage_attributes(attribute_tag[i], uv, but, bst, des)
            attr_objects.append(a)
            attr_exists.add(_hash)
        return attr_objects

    def stage_attributes(self, attribute: str, unit_value: str,
                         bespoke_unit_tag: int, bespoke_sub_theme: int,
                         description: str) -> db.Model:
        """
        Stage Attributes
        :param attribute: Attribute
        :param unit_value: Unit Value
        :param bespoke_unit_tag: Unit Id
        :param bespoke_sub_theme: SubTheme Id
        :param description: Attributes Description
        :return: Attribute instance
        """
        _a = Attributes._get_by_name_unit_unitvalue(attribute, bespoke_unit_tag, unit_value)
        if _a:
            logger.info('{} attribute with Unit ID: {} and Unit Value: {} already exists'.format(attribute,
                                                                                                 str(bespoke_unit_tag),
                                                                                                 unit_value))
            return _a
        a = Attributes(id=str(uuid.uuid4()), name=attribute,
                       table_name=(attribute + '_' + str(uuid.uuid4()).replace('-', '_')),
                       sub_theme=bespoke_sub_theme, unit=bespoke_unit_tag,
                       unit_value=str(unit_value), description=description)
        a = a.save()
        return a

    def save_attr_sensor(self, attrs, sensors) -> None:
        """
        Save Attributes and Sensors
        :param attrs: Attributes
        :param sensors: Seansors
        """

        for sensor in sensors:
            for attr in attrs:
                _sa = SensorAttribute._get_by_sid_aid(sensor.id, attr.id)
                if _sa:
                    logger.info('Sensor ID: %s, Attribute Id: %s already exists' % (_sa.s_id, _sa.a_id))
                    continue

                sa = SensorAttribute(sensor.id, attr.id)
                sa.save()

    def create_tables(self, attributes: [db.Model]) -> None:
        """
        Create Data Base Tables
        :param attributes: Attributes
        """
        table_query = db.session.execute("select * from pg_catalog.pg_tables")
        table_tuples = table_query.fetchall()
        tables = set()
        for t in table_tuples:
            tables.add(t[1])

        for attr in attributes:
            if attr.table_name.lower() not in tables:
                db.session.execute(
                    'CREATE TABLE %s (s_id TEXT NOT NULL, value TEXT NOT NULL, api_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, timestamp TIMESTAMP WITHOUT TIME ZONE, PRIMARY KEY(s_id, value, api_timestamp))' % (
                        attr.table_name))
                logger.info('Created Table', attr.table_name.lower())

            else:
                logger.info('{} already exists'.format(attr.table_name.replace('-', '_')))

    def insert_data(self, attr_objects: [db.Model], sensor_objects: [db.Model], dataframe: pd.DataFrame,
                    sensor_tag: str, sensor_prefix: str, api_timestamp_tag: str,
                    attr_value_tag: Union[str, None] = None,
                    attribute_tag: Union[str, None] = None, unit_value_tag: Union[str, None] = None) -> None:
        """
        Insert Data in to tables
        :param attr_objects: List of attributes
        :param sensor_objects: list of sensors
        :param dataframe: Pandas DataFrame
        :param sensor_tag: sensor tag
        :param sensor_prefix: sensor name prefix
        :param api_timestamp_tag: timestamp tag
        :param attr_value_tag: Attribute value tag
        :param attribute_tag: Attribute tag
        :param unit_value_tag: Unit Value tag
        """
        db.metadata.clear()
        sensors = dataframe[sensor_tag].tolist()
        value_exists = set()
        _classes = []

        api_timestamp = []
        if api_timestamp_tag is not None:
            api_timestamp = dataframe[api_timestamp_tag].tolist()

        for attr in attr_objects:
            _values = []
            if attr_value_tag is not None:
                _dataframe = None
                if unit_value_tag is not None:
                    _dataframe = dataframe[
                        (dataframe[attribute_tag] == attr.name) & (dataframe[unit_value_tag] == attr.unit_value)]
                else:
                    _dataframe = dataframe[dataframe[attribute_tag] == attr.name]

                _values = _dataframe[attr_value_tag].tolist()
                sensors = _dataframe[sensor_tag].tolist()

            model = ModelClass(attr.table_name.lower())
            _classes.append(model)
            values = []
            models = []

            if attr_value_tag is None:
                values = dataframe[attr.name].tolist()
            else:
                values = _values

            for i in range(len(values)):
                sensor_name = sensors[i]
                sensor_id = sensor_objects[sensor_prefix + str(sensor_name)].id

                a_date = None
                if len(api_timestamp) > 0 and api_timestamp[i]:
                    a_date = convert_unix_to_timestamp(str(api_timestamp[i]))
                    _, a_date = convert_to_date(a_date)

                if a_date is None:
                    a_date = datetime.utcnow()

                _hash = self._hash_it(sensor_prefix + str(sensor_name), str(values[i]), str(a_date))
                if _hash in value_exists:
                    continue

                m = model()
                m.s_id = sensor_id
                m.value = values[i]
                m.api_timestamp = a_date
                m.timestamp = datetime.utcnow()
                models.append(m)

                try:
                    if i % 10 == 0:
                        db.session.add_all(models)
                        db.session.commit()
                except IntegrityError as e:
                    db.session.rollback()
                    logger.info(
                        'Sensor id: %s with value %s at time %s already exists' % (sensor_id, values[i], a_date))

                value_exists.add(_hash)

            db.session.add_all(models)

        try:
            db.session.commit()
            for _class in _classes:
                sqlalchemy.orm.instrumentation.unregister_class(_class)
                del _class._decl_class_registry[_class.__name__]
        except IntegrityError as e:
            db.session.rollback()
            logger.info('Unable to save certain values as they already are in the system, check logs')

    def _hash_it(self, *args: [Any]) -> int:
        """
        Create hash of variable arguments list
        :param args: variable arguments
        :return: Hash of the variable arguments
        """
        to_hash = ''
        for a in args:
            to_hash += a

        return abs(hash(to_hash)) % (10 ** 8)

    def stage_api_commit(self) -> int:
        """
        Stage API commit to database
        :return: Api identification number
        """

        api = API(name=self.api_name,
                  url=self.url, refresh_time=self.refresh_time,
                  token_expiry=self.token_expiry,
                  api_key=self.api_key, api_class=self.api_class)
        _api = api.save()
        return _api.id

    def create_unit(self, _type: str, description: str) -> db.Model:
        """
        Create Unit
        :param _type: Unit type
        :param description: Description of unit
        :return: Unit

        """
        unit = Unit(_type=_type, description=description)
        unit.save()
        return unit

    def create_theme(self, name: str) -> db.Model:
        """
        Create Theme
        :param name: Name of theme
        :return: Theme
        """
        theme = Theme(name=name)
        theme.save()
        return theme

    def create_subtheme(self, theme_id: str, name: str) -> db.Model:
        """
        Create new SubTheme
        :param theme_id: Theme id
        :param name: SubTheme name
        :return: Subtheme
        """
        sub_theme = SubTheme(t_id=theme_id, name=name)
        sub_theme.save()
        return sub_theme

    def commit(self) -> None:
        """
        Commit change to database
        """
        db.session.commit()


class Location(object):
    """
    Location Object
    """

    def __init__(self, lat: str, lon: str):
        self.lat = lat
        self.lon = lon
