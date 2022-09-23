# carbonintensity-forked

<!-- badges start -->

[![Maintained][Maintained]](#)

<!-- badges end -->

_Simple Carbon Intensity UK API Library_

The purpose of this library is to retrieve information from [Carbon Intensity UK](https://carbonintensity.org.uk/)

The client connects asynchronously to the API, retrieving information about the current level of CO2 generating energy in the current period.

It uses `aiohttp` to communicate with the API asynchronously. This decision has been based mainly on the premise that the library will be used in the context of Home Assistant integration.

In addition it calculates when is the next 24 hours lowest level comparing values of the CO2 forecast levels.

This version also adds in a regional low carbon generation percentage, which is calculated as nuclear + wind + solar + biomass + hydro as well as the work by @jfparis to implement optimal windows/forecasts. 

## Example

Retrieve regional and national information based on postcode `SW1` for the next 24 hours starting now:

```python
   client = Client("SW1")
   response = await client.async_get_data()
   data = response["data"]
```
Note: Time in UTC

## Data format

An example of the function output can be found below:

```json
   {
       "data":
        {
              "current_period_from": "2020-05-20T10:00+00:00",
              "current_period_to": "2020-05-20T10:30+00:00",
              "current_period_forecast":300,
              "current_period_index": "high",
              "current_period_national_forecast":230,
              "current_period_national_index": "moderate",
              "current_low_carbon_percentage": 23,
              "lowest_period_from":"2020-05-21T14:00+00:00",
              "lowest_period_to":"2020-05-21T14:30+00:00",
              "lowest_period_forecast": 168,
              "lowest_period_index": "moderate",
              "optimal_window_from" : "2020-05-20T10:00+00:00",
              "optimal_window_to" : "2020-05-20T10:30+00:00",
              "optimal_window_forecast" : 121,
              "optimal_window_index" : "low",
              "optimal_window_48_from" : "2020-05-20T10:00+00:00",
              "optimal_window_48_to" : "2020-05-20T10:30+00:00",
              "optimal_window_48_forecast" : 130,
              "optimal_window_48_index" : "low"
              "postcode": "SW1"
        }
    }
```

## Install carbonintensity

```bash
python3 -m pip install -U carbonintensity-forked
```

<!-- links start -->

[maintained]: https://img.shields.io/maintenance/yes/2020.svg

<!-- links end -->

## Licenses

This work is based on the following:
- [carbonintensity](https://github.com/jscruz/carbonintensity): See [License](https://github.com/jscruz/carbonintensity/blob/master/LICENSE)
- [sensor.carbon_intensity_uk](https://github.com/jfparis/sensor.carbon_intensity_uk)
- [sampleclient](https://github.com/ludeeus/sampleclient): See [Original license](./licenses/sampleclient/LICENSE)
- [Carbon Intensity API](https://carbonintensity.org.uk/): See [Terms and conditions](https://github.com/carbon-intensity/terms/)

