# habitat-fydp-package

### Purpose of the Package
Democratize access to HAB related data in Lake Erie to be used for scientific research. 

### Features

Listed API function currently available are listed below: 

```
|    | SDK Function                                                                         | Description                                 | Purpose      |
|---:|:-------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:-------------|
|  0 | list_stations()                                                                      | List all the stations on Lake Erie with its respective coordinate              | Consume Data |
|  1 | list_measurement_defintion(measurement = None)                                       | List all the measurements that are measured                                    | Consume Data |
|  2 | list_station_measurment_types(station_name)                                          | List all the measurements taken at a specific station                            | Consume Data |
|  3 | get_most_recent_measurement(station_name, measurement)                               | Get the most up-to-date for given measurement and station                     | Consume Data |
|  4 | get_historical_measurements(station_name, measurement, start_date, end_date)         | Get a range of measurements given a time range, measurement and station         | Consume Data |
|  5 | plot_lake_depth()                                                                    | Shows that different depth levels in Lake Erie                                   | Consume Data |
|  6 | get_weather_variables(start_date, end_date, station_name, freq)                      | Returns the measured weather variables needed for HAB monitoring         | Consume Data |
|  7 | aggregate_habnet_data(station_name, measurement, start_date, end_date,freq,path_)    | Links all data sources together for a station into one dataframe                  | Consume Data |
|  8 | smooth_timeseries_measurement(station_name, measurement, start_date, end_date)       | Smooths the time series for a specific measurement and station            | Analyze Data |
|  9 | decomposition_timeseries_measurment(station_name, measurement, start_date, end_date) | Decomposes the time series for a specific measurement and station            | Analyze Data |
| 10 | univariate_forecast_arima(series, horizon, frequency_of_obvs)                        | Forecasts a specific measurement for a given station based on its historical data | Analyze Data |
``` 


### Getting Started

Getting started is easy! Just pip install our package as below: 

```
pip install habitat-fydp-package
```

To test if the package downloaded try this! 

```python

import habitat_fydp_package 
from habitat_fydp_package import list_station_measurment_types
list_station_measurment_types('Toledo Pump Station')

``` 

### Usage 

Call help on any of the functions listed in the table to return docstring and information on inputs / oupus for a particular function!