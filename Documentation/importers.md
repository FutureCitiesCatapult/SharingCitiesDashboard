# Importers
Within the context of SharingCitiesDashboard, importers are the means of adding a particular data source in the system as well as populating the database with values. New importers inherit from a base class containing methods that allow the user to specify the theme, subtheme, sensors, attributes and values of a data source, and save these in the database ensuring that there are no conflicts/duplicates. Sensitive importer specification is provided by the user using the importer specifications YAML file:

```bash
 api_endpoints:
  air_quality:
    API_CLASS: importers.air_quality.KCLAirQuality
    API_KEY: ''
    API_NAME: Air_Quality_KCL
    BASE_URL: YOUR_URL
    REFRESH_TIME: 3600
    REFRESH_URL: null
    TOKEN_EXPIRY: null
```

In the example above, the user importer class is named ```KCLAirQuality``` located under ```air_quality```. More information related to importer use can be found here.  

### Pre-build importers
Presently, there are pre-build importers for the following two cities: Greenwich and Milan. For Lisbon, an importer using test data for *GiraStation* is created as a proof of concept.

#### Greenwich
SharingCities Dashboard Greenwich importers were created using a dedicated ArcGIS REST API Services Directory which was provided as a proof of concept to source the following datasets:

* Smart parking stations with various attributes (coordinates, street name, parking type etc.). Historical occupation data for these stations were also provided with various attributes (availability, status etc.). Currently there are two implementations, a test one referring to stations located in Oxford, and a live one referring to stations in Greenwich. 

API/data sample name | Description | Importer | Status | Endpoint 
--- | --- | --- | --- | ---
Greenwich smart parking metadata | Location and metadata relating to each parking Lot, each Lot contains a number of parking bays. There are 20 Lots and 46 bays in total. Data table is updated (truncated) each time the api is called | GreenwichMeta_2 | Live | https://maps.london.gov.uk/gla/rest/services/apps/smart_parking_demo_service_01/MapServer/7/
Greenwich smart parking occupancy | Occupancy information relating to each parking Lot i.e. number available. Rows of data are appended to the table each time the api is called | GreenwichOCC_2 | Live | https://maps.london.gov.uk/gla/rest/services/apps/smart_parking_demo_service_01/MapServer/8/
Oxford smart parking metadata | Location and metadata relating to each parking Lot, each Lot contains a number of parking bays. This was sample data relating to Oxford and was used until the Greenwich data came on stream | GreenwichMeta | Tested with Sample | https://maps.london.gov.uk/gla/rest/services/apps/smart_parking_demo_service_01/MapServer/0/
Oxford smart parking occupancy | Occupancy information relating to each parking Lot i.e. number available. Rows of data are appended to the table each time the api is called. | GreenwichOCC | Tested with Sample | https://maps.london.gov.uk/gla/rest/services/apps/smart_parking_demo_service_01/MapServer/1/

Below a more detailed description of the associated attributes is given.

Attribute | Importer | Unit | Description 
--- | --- | --- | --- 
baycount, baycount_2 | GreenwichMeta, GreenwichMeta_2 | count | Number of parking bays in the parking lot
baytype, baytype_2 | GreenwichMeta, GreenwichMeta_2 | Categorical | Type of bay
free, free_2 | GreenwichOCC, GreenwichOCC_2 | count | Count of free spaces isoffline, isoffline_2 | GreenwichOCC, GreenwichOCC_2 | binary | Flag indicating sensor status
occupied, occupied_2 | GreenwichOCC, GreenwichOCC_2 | count | Number of occupied spaces

* Energy related data (energy consumption, flow rate, temperature out etc.) for the Ernest Dense estate in Greenwich as well as residential energy consumption data. 

API/data sample name | Description | Importer | Status | Endpoint 
--- | --- | --- | --- | ---
Ernest Dence Boiler House boiler | Boiler energy consumption (kWh) by minute. Sample data. | GreenwichKiwiPump | data from 1/9/18 to 8/9/18 | https://maps.london.gov.uk/gla/rest/services/apps/smart_parking_demo_service_01/MapServer/6/
Siemens Boiler metrics | Metrics for three boilers: energy consumption (kWh), flow rate (m3/h), temperature out (degrees C), temperature return (degrees C) | GreenwichSiemens | data from 8/2/18 to 7/02/18 | https://maps.london.gov.uk/gla/rest/services/apps/smart_parking_demo_service_01/MapServer/3/
Residential sample | Residential house sample energy consumption (Wm) and mean room luminous/temperature data. Sample data. | GreenwichWholeHouse | data from 1/9/18 to 8/9/18 | https://maps.london.gov.uk/gla/rest/services/apps/smart_parking_demo_service_01/MapServer/4/

The attribute data related to each importer are shown in the table below. Sharing Cities dashboard allows the definition of different measurement units through the implementation of each importer. All attributes are associated with corresponding sensors.

Attribute | Importer | Unit | Description 
--- | --- | --- | --- 
b*_heat_vaue | GreenwichSiemens | kWh | Energy consumption
b*_flow_vaue | GreenwichSiemens | m3/h | Energy flow rate
b*_temp_out_value | GreenwichSiemens | C | Temperature out
b*_temp_back_value | GreenwichSiemens | C | Temperature return
power_sid | GreenwichWholeHouse | Wm | Energy consumption
avg_lux | GreenwichWholeHouse | Lux	Mean | room luminocity
temp_sid | GreenwichWholeHouse | C | Mean room temperature
value_kw | GreenwichKiwiPump | kWh | Energy | consumption

#### Milan
Currently, there are four API groups associated with SharingCities Dashboard relevant to Milan:
* SC_EMOBILITY_Refeel. Refeel API to get data bout two e-car available to condominium locate in viale Bacchiglione 
* SC_EMSmonet_ConsumiEnergetici. Test API for Monet SEMS. 
* SC_LAMPPOST_SensoriMeteo. REST API to retrieve data from lamp post sensors on the Sharing cities area 
* SC_PARKING_Kiunsys. REST API to get data related to Parking Area by Kiunsys. 

API/data sample name | Description | Importer | Status | Endpoint 
--- | --- | --- | --- | ---
e-mobility refeel data | Information on activities relted to two e-car used by the inhabitants of a condominium located in viale Bacchiglione. The e-car plates are attributed as sensors having coordinates the centroid of viale Bacchiglione. | Milan_API_sc_emobility_refeel | Live | https://api.comune.milano.it:443/SC_EMOBILITY_Refeel/1.0 
energy management data | Test API for Monet SEMS. | MilanAPI | API subscription status is rejected and as a result importing is not available | https://api.comune.milano.it:443/SC_EMSmonet_ConsumiEnergetici/1.0/
Environmental sensors on lampposts | Information related to the location of the sensors as well as temperature, pressure and humidity | Milan_API_sensori_meteo_meta, Milan_API_sensori_meteo | Live | https://api.comune.milano.it:443/SC_LAMPPOST_SensoriMeteo/1.0/dati_meteo?
Smart parking sensors | Location, type and occupancy information for smart parking sensors | Milan_API_sc_parking_kiunsys_meta Milan_API_sc_parking_kiunsys | Live | https://api.comune.milano.it:443/SC_PARKING_Kiunsys/1.0/parkingArea/SHCS02001/parkingSpotSensorsStatus?

Below the associated attributes for each importer are given:

Attribute | Importer | Unit | Description 
--- | --- | --- | --- 
parkingSpotType | Milan_API_sc_parking_kiunsys_meta | Categorical | Parking spot type
positionOnMap | Milan_API_sc_parking_kiunsys_meta | Numerical sensor identifier. Links to the sensor’s coordinates | Location of sensor
state | Milan_API_sc_parking_kiunsys | Binary | Sensor’s occupancy flag
rentalState | Milan_API_sc_emobility_refeel | Categorical | Information related to booking state of e-cars
duration | Milan_API_sc_emobility_refeel | minutes | Duration between two subsequent booking state changes
pressione | Milan_API_sensori_meteo | mB | Atmospheric pressure
temperatura | Milan_API_sensori_meteo | C | Temperature
umidita | Milan_API_sensori_meteo | N/A | Humidity
temperature, dimmer_perc, dimmer_read, dimmer_default, dimmer_set, do2,tilt_angle, connected_device energy_delivered,di4, di5, energy_consumed, do1, di1, di2, di3 | MilanAPI | API subscription status is rejected and as a result importing is not available | N/A | Lampost environmental sensors

#### Lisbon
AlticeLabs are an organisation that are representing / owning Lisbon's USP. From a technical perspective, they have developed the most feature rich API. However, it is designed to enable Device-2-Device communication and is less designed for consumption of the data. Though this documentation is helpful - it does not provide much context on the specific Sharing Cities Data. 
As a result, there are currently no data retrieving importers operational. As a proof of concept, a generic importer was prepared based on a sample of GiraStation devices (bike docks).

API/data sample name | Description | Importer | Status | Endpoint 
--- | --- | --- | --- | ---
GiraStation | Location of bike stations | LisbonAPI | Sample only | N/A

### Building an importer
Building a SharingCities Dashboard importer implies implementing a python class, which inherits methods from [BaseImporter](https://github.com/FutureCitiesCatapult/SharingCitiesDashboard/blob/thanosbnt-patch-1-1/Analytics/importers/base.py) class. 
The methods in this class provide the means to save all different database components of the Dashboard, as well as helper functions. The example below can be viewed as a walkthrough to the process of making an importer.

First, the relevant entries in config.yml file need to be created:

#### Step 1: Filling the relevant entries in config.yml
```bash
api_endpoints:
  template_importer:
    API_CLASS: importers.TemplateImporter
    API_KEY: ''
    API_NAME: template_importer
    BASE_URL: <IMPORTER-ENDPOINT>
    REFRESH_TIME: 300
    REFRESH_URL: null
    TOKEN_EXPIRY: null
```

After doing this, the importer class can be implemented:

#### Step 2: Importing the relevant libraries that will be used.
```python
from importers.base import BaseImporter, Location, get_config
from models.sensor import Sensor
from models import location
from .state_decorator import ImporterStatus, Status

from db import db
import pandas as pd
import numpy as np
```

#### Step 3: Creating the importer class
```python
### Decorators linking to the config.yml file. TemplateImporter is the importer python class, api_endpoints is the relevant header in the config.env.yml and template_importer is the header of the configuration variables for that importer
@GetConfig("TemplateImporter", 'api_endpoints', 'template_importer') 
class TemplateImporter(BaseImporter): ### The template importer inherits the methods of the BaseImporter class

    ### Gets the current statis of the importer (eg. success, failure)
    importer_status = ImporterStatus.get_importer_status() 

    ### Gets Importer Config, and instantiate BaseImporter
    def __init__(self) -> None:
  
        super().__init__(self.API_NAME, self.BASE_URL, self.REFRESH_TIME,
                         self.API_KEY, self.API_CLASS,
                         self.TOKEN_EXPIRY)

    ### Decorator linking to methods for updating the attribute ranges
    @update_attribute_ranges
    def _create_datasource(self, headers: Union[str, None] = None) -> None: 
        ### _create_datasource is a method from BaseImporter that invokes requests to fetch the data from the API
        try:
            super()._create_datasource(headers)

            ### create_dataframe  will parse the json response and return the data in a tabular format (dataframe)
            ### the argument ignore_object_tags will ignore the objects that are assigned to those tags
            ### see json_reader.py for more options
            self.df = self.create_dataframe(ignore_object_tags=['info', 'fields'])

            ### Creating a location object and passing the relevant coordinate columns
            loc = Location('latitude', 'longitude')

            ### A description for the importer. 
            self.df['description'] = 'a template importer'

            ### Passing, the dataframe as well as the relevant attributes, units, descriptionds api timestamps 
            self.create_datasource(dataframe=self.df, sensor_tag='<THE-SENSOR-ID>', attribute_tag=['<SENSOR-ATTRIBUTE-1>', '<SENSOR-ATTRIBUTE-2>'],
                                   unit_value=['<UNIT-VALUE-1>', '<UNIT-VALUE-2>'], bespoke_unit_tag=['<FILL-IN-HERE-IF-UNIT-NOT-IN-DB>'], description=['description'], bespoke_sub_theme=[],
                                   location_tag=loc, sensor_prefix='template_importer_sensor_', api_timestamp_tag='<THE-API-TIMESTAMP>',
                                   is_dependent='<TRUE-IF-SENSOR/LOCATION-ALREADY-IN-DB>')

            self.importer_status.status = Status.success(__class__.__name__)

        ### Catch and log any errors
        except Exception as e:

            self.importer_status.status = Status.failure(__class__.__name__, e.__str__(), traceback.format_exc())


```
