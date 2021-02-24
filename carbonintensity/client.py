"""Client."""
from datetime import datetime, timezone
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


class Client:
    """Carbon Intensity API Client"""

    def __init__(self, postcode):
        self.postcode = postcode
        self.headers = {"Accept": "application/json"}
        _LOGGER.debug(str(self))

    def __str__(self):
        return "{ postcode: %s, headers: %s }" % (self.postcode, self.headers)

    async def async_get_data(self, from_time=None):
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
        _LOGGER.debug("Regional Request: %s" % request_url)
        _LOGGER.debug("National Request: %s" % request_url_national)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_response = await resp.json()
            async with session.get(request_url_national) as resp:
                json_response_national = await resp.json()            
            return generate_response(json_response, json_response_national)


def generate_response(json_response, json_response_national):
    periods = dict()
    response = {}
    _LOGGER.debug(json_response)
    _LOGGER.debug(json_response_national)
    data = json_response["data"]["data"]
    postcode = json_response["data"]["postcode"]
    for period in data:
        periods[period["intensity"]["forecast"]] = {
            "from": period["from"],
            "to": period["to"],
            "index": period["intensity"]["index"],
        }
    national_data = json_response_national["data"]
    minimum_key = min(periods.keys())

    response = {
        "data": {
            "current_period_from": datetime.strptime(
                data[0]["from"], "%Y-%m-%dT%H:%MZ"
            ).replace(tzinfo=timezone.utc),
            "current_period_to": datetime.strptime(
                data[0]["to"], "%Y-%m-%dT%H:%MZ"
            ).replace(tzinfo=timezone.utc),
            "current_period_forecast": data[0]["intensity"]["forecast"],
            "current_period_index": data[0]["intensity"]["index"],
            "current_period_national_forecast": national_data[0]["intensity"]["forecast"],
            "current_period_national_index": national_data[0]["intensity"]["index"],
            "lowest_period_from": datetime.strptime(
                periods[minimum_key]["from"], "%Y-%m-%dT%H:%MZ"
            ).replace(tzinfo=timezone.utc),
            "lowest_period_to": datetime.strptime(
                periods[minimum_key]["to"], "%Y-%m-%dT%H:%MZ"
            ).replace(tzinfo=timezone.utc),
            "lowest_period_forecast": minimum_key,
            "lowest_period_index": periods[minimum_key]["index"],
            "unit": "gCO2/kWh",
            "postcode": postcode,
        }
    }
    return response
