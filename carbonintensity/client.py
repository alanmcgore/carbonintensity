"""Client."""
from datetime import datetime, timezone
import logging
import aiohttp
import numpy as np

_LOGGER = logging.getLogger(__name__)

INTENSITY = {
    "very low" : 0,
    "low" : 1,
    "moderate": 2,
    "high": 3,
    "very high": 4,
}

INTENSITY_INDEXES = {
    2021: [50, 140, 220, 330],
    2022: [45, 130, 210, 310],
    2023: [40, 120, 200, 290],
    2024: [35, 110, 190, 270],
    2025: [30, 100, 180, 250],
    2026: [25, 90, 170, 230],
    2027: [20, 80, 160, 210],
    2028: [15, 70, 150, 190],
    2029: [10, 60, 140, 170],
    2030: [5, 50, 130, 150],
}

LOW_CARBON_SOURCES = ["biomass", "nuclear", "hydro", "solar", "wind"]

class Client:
    """Carbon Intensity API Client"""

    def __init__(self, postcode):
        self.postcode = postcode
        self.headers = {"Accept": "application/json"}
        _LOGGER.debug(str(self))

    def __str__(self):
        return f"{{ postcode: {self.postcode}, headers: {self.headers} }}"

    async def async_get_data(self, from_time=None):
        ''' Get's national and regional electric grid co2
        intensity data from carbonintensity.org.uk '''
        if from_time is None:
            from_time = datetime.now()
        request_url = (
            "https://api.carbonintensity.org.uk/regional/intensity/%s/fw24h/postcode/%s"
            % (from_time.strftime("%Y-%m-%dT%H:%MZ"), self.postcode)
        )
        request_url_national = (
            "https://api.carbonintensity.org.uk/intensity/%s/fw24h/"
            % (from_time.strftime("%Y-%m-%dT%H:%MZ"))
        )
        _LOGGER.debug("Regional Request: %s", request_url)
        _LOGGER.debug("National Request: %s", request_url_national)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_response = await resp.json()
            async with session.get(request_url_national) as resp:
                json_response_national = await resp.json()         
            return generate_response(json_response, json_response_national)

def generate_response(json_response, json_response_national):
    ''' Generates JSON response containing processed intensity data '''
    intensities = []
    period_start = []
    period_end = []
    periods = dict()
    response = {}
    _LOGGER.debug(json_response)
    _LOGGER.debug(json_response_national)
    data = json_response["data"]["data"]
    postcode = json_response["data"]["postcode"]

    national_data = json_response_national["data"]
    two_day_forecast = True

    current_intensity_index = INTENSITY_INDEXES[datetime.now().year]
    def get_index(intensity):
        if intensity < current_intensity_index[0]:
            return "very low"
        elif intensity < current_intensity_index[1]:
            return "low"
        elif intensity < current_intensity_index[2]:
            return "moderate"
        elif intensity < current_intensity_index[3]:
            return "high"
        else:
            return "very high"

     # sanitise input length
    if datetime.strptime(data[0]["to"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc) < datetime.utcnow().replace(tzinfo=timezone.utc):
        data.pop(0)
    if len(data) > 96:
        data = data[0:96]
    if len(data) < 48:
        return {"error": "malformed data"}
    if len(data) % 2 == 1:
        data.pop(-1)
    if len(data) < 56:
        two_day_forecast = False

    for period in data:
        periods[period["intensity"]["forecast"]] = {
            "from": period["from"],
            "to": period["to"],
            "index": period["intensity"]["index"],
        }

    for period in data:
        period_start.append(datetime.strptime(
                period["from"], "%Y-%m-%dT%H:%MZ"
            ).replace(tzinfo=timezone.utc))
        period_end.append(datetime.strptime(
                period["to"], "%Y-%m-%dT%H:%MZ"
            ).replace(tzinfo=timezone.utc))
        intensities.append(period["intensity"]["forecast"])
 
    minimum_key = min(periods.keys())
    intensity_array = np.array(intensities)
    hourly_intensities = np.convolve(intensity_array, np.ones(2)/2 , 'valid')[::2]

    hours_start = period_start[::2]
    hours_end = period_end[1::2]

    average_intensity24h  = np.convolve(hourly_intensities[:24], np.ones(4)/4 , 'valid')
    best24h = np.argmin(average_intensity24h)

    if two_day_forecast:
        average_intensity48h  = np.convolve(hourly_intensities[24:], np.ones(4)/4 , 'valid')
        best48h = np.argmin(average_intensity48h)
    else:
        best48h = 0

    hourly_forecast = []
    for i, start_hour in enumerate(hours_start):
        hourly_forecast.append({
            "from":      start_hour,
            "to":        hours_end[i],
            "intensity": hourly_intensities[i],
            "index":     get_index(hourly_intensities[i]),
            "optimal":   True if (start_hour>=hours_start[best24h] and hours_end[i]<=hours_end[best24h+3]) or \
                                 (two_day_forecast and start_hour>=hours_start[best48h+24] 
                                 and hours_end[i]<=hours_end[best48h+3+24]) else False,
        })

    low_carbon_percentage = 0
    for i in data[0]["generationmix"]:
        if i["fuel"] in LOW_CARBON_SOURCES:
            low_carbon_percentage += i["perc"]
    

    response = {
        "data": {
            "current_period_from": datetime.fromisoformat(data[0]["from"].replace('Z','+00:00')),
            "current_period_to": datetime.fromisoformat(data[0]["to"].replace('Z','+00:00')),
            "current_period_forecast": data[0]["intensity"]["forecast"],
            "current_period_index": data[0]["intensity"]["index"],
            "current_period_national_forecast": national_data[0]["intensity"]["forecast"],
            "current_period_national_index": national_data[0]["intensity"]["index"],
            "current_low_carbon_percentage": low_carbon_percentage,
            "lowest_period_from": datetime.fromisoformat(
                periods[minimum_key]["from"].replace('Z','+00:00')),
            "lowest_period_to": datetime.fromisoformat(
                periods[minimum_key]["to"].replace('Z','+00:00')),
            "lowest_period_forecast": minimum_key,
            "lowest_period_index": periods[minimum_key]["index"],
            "optimal_window_from" : hours_start[best24h],
            "optimal_window_to" : hours_end[best24h+3],
            "optimal_window_forecast" : average_intensity24h[best24h],
            "optimal_window_index" : get_index(average_intensity24h[best24h]),
            "optimal_window_48_from" : hours_start[best48h+24] if two_day_forecast else None,
            "optimal_window_48_to" : hours_end[best48h+3+24] if two_day_forecast else None,
            "optimal_window_48_forecast" : average_intensity48h[best48h] if two_day_forecast else None, # no need for +24 as we are reading from a reduced array
            "optimal_window_48_index" : get_index(average_intensity48h[best48h]) if two_day_forecast else None,
            "unit": "gCO2/kWh",
            "forecast": hourly_forecast,
            "postcode": postcode,
                    }
    }
    return response
