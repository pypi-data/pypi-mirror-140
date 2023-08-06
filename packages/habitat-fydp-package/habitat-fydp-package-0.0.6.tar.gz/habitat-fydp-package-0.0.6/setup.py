# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['habitat_fydp_package']

package_data = \
{'': ['*'], 'habitat_fydp_package': ['Lake_Erie_Contours/*']}

install_requires = \
['DateTime>=4.3,<5.0',
 'folium>=0.12.1,<0.13.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy==1.19.3',
 'pandas==1',
 'pmdarima>=1.8.4,<2.0.0',
 'pyshp>=2.1.3,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'sklearn>=0.0,<0.1',
 'wwo-hist>=0.0.7,<0.0.8']

setup_kwargs = {
    'name': 'habitat-fydp-package',
    'version': '0.0.6',
    'description': 'Democratize access to HAB related data in Lake Erie to be used for scientific research',
    'long_description': "# habitat-fydp-package\n\n### Purpose of the Package\nDemocratize access to HAB related data in Lake Erie to be used for scientific research. \n\n### Features\n\nListed API function currently available are listed below: \n\n```\n|    | SDK Function                                                                         | Description                                 | Purpose      |\n|---:|:-------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:-------------|\n|  0 | list_stations()                                                                      | List all the stations on Lake Erie with its respective coordinate              | Consume Data |\n|  1 | list_measurement_defintion(measurement = None)                                       | List all the measurements that are measured                                    | Consume Data |\n|  2 | list_station_measurment_types(station_name)                                          | List all the measurements taken at a specific station                            | Consume Data |\n|  3 | get_most_recent_measurement(station_name, measurement)                               | Get the most up-to-date for given measurement and station                     | Consume Data |\n|  4 | get_historical_measurements(station_name, measurement, start_date, end_date)         | Get a range of measurements given a time range, measurement and station         | Consume Data |\n|  5 | plot_lake_depth()                                                                    | Shows that different depth levels in Lake Erie                                   | Consume Data |\n|  6 | get_weather_variables(start_date, end_date, station_name, freq)                      | Returns the measured weather variables needed for HAB monitoring         | Consume Data |\n|  7 | aggregate_habnet_data(station_name, measurement, start_date, end_date,freq,path_)    | Links all data sources together for a station into one dataframe                  | Consume Data |\n|  8 | smooth_timeseries_measurement(station_name, measurement, start_date, end_date)       | Smooths the time series for a specific measurement and station            | Analyze Data |\n|  9 | decomposition_timeseries_measurment(station_name, measurement, start_date, end_date) | Decomposes the time series for a specific measurement and station            | Analyze Data |\n| 10 | univariate_forecast_arima(series, horizon, frequency_of_obvs)                        | Forecasts a specific measurement for a given station based on its historical data | Analyze Data |\n``` \n\n\n### Getting Started\n\nGetting started is easy! Just pip install our package as below: \n\n```\npip install habitat-fydp-package\n```\n\nTo test if the package downloaded try this! \n\n```python\n\nimport habitat_fydp_package \nfrom habitat_fydp_package import list_station_measurment_types\nlist_station_measurment_types('Toledo Pump Station')\n\n``` \n\n### Usage \n\nCall help on any of the functions listed in the table to return docstring and information on inputs / oupus for a particular function!",
    'author': 'Shanthosh Pushparajah',
    'author_email': 'spushpar@uwaterloo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cognitetosh/habitat-fydp-package',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.8',
}


setup(**setup_kwargs)
