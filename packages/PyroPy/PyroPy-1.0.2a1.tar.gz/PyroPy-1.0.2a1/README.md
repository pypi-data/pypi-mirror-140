# PyroPy
Analysis of fire spread and intensity.

Author: Geoffysicist

Source code: [https://github.com/Geoffysicist/PyroPy](https://github.com/Geoffysicist/PyroPy)

Uses weather data and model specific parameters to predict rate of spread and
intensity of wildfires.

Unless otherwise indicated all models have been taken from:
> Cruz, Miguel, James Gould, Martin Alexander, Lachie Mccaw, and 
Stuart Matthews. (2015) *A Guide to Rate of Fire Spread Models for Australian 
Vegetation*, CSIRO Land & Water and AFAC, Melbourne, Vic 125 pp. 


## Install
```
pip install PyroPy
```

## Included modules
 - `firebehaviour`: Defines the main `Incident` class and several auxillary 
        dictionaries. An `Incident` stores data related to the incident 
        including weather, model parameters and model outputs.
 - `spreadmodels`: fire spread model functions which can be called directly or 
        by an `Incident`.
 - `weatherdata`: functions for reading, writing and transforming weather 
        between various formats including Australian Bureau of Meteorology 
        (BoM) Gridded Weather, BoM Observations (*.axf) and Amicus.


for more detailed information see 
[modules](https://geoffysicist.github.io/PyroPy/modules/).

## Typical Use Example
```python
from pyropy import firebehaviour as fb
from pyropy import weatherdata as wd

if __name__ == '__main__':
   #read the weather data into a pandas DataFrame
   weather_fn = 'tests/.data/weather_gridded_in.csv'
   weather_df = wd.gridded_to_df(weather_fn)

   #create an Incident using the weather data
   incident = fb.Incident(weather_df)

   #add the parameters necessary to run the desired models
   incident_params = {
      #forest_mk5
      'wrf': 3.5,
      'fuel_load': 15,
      #forest_vesta
      'fhs_surf': 3.5,
      'fhs_n_surf': 2,
      'fuel_height_ns': 20
   }
   incident.update_params(incident_params)

   #run the desired models
   incident.run_forest_mk5()
   incident.run_forest_vesta()

   #output results
   incident.print()
```
