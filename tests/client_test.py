from carbonintensity.client import Client, generate_response
import pytest
from datetime import datetime, timezone, date
import os
import json

TESTRESPONSE_FILENAME = os.path.join(os.path.dirname(__file__), "response.json")
TESTRESPONSENATIONAL_FILENAME = os.path.join(os.path.dirname(__file__), "response_national.json")


def test_string_format():
    client = Client("BH1")
    assert client.postcode == "BH1"
    assert client.headers == {"Accept": "application/json"}


def test_generate_response():
    response = {}
    datetime.strptime
    with open(TESTRESPONSE_FILENAME) as json_file, open(TESTRESPONSENATIONAL_FILENAME) as json_national_file:
        json_response = json.load(json_file)
        json_national_response = json.load(json_national_file)
        response = generate_response(json_response, json_national_response)

    data = response["data"]
    assert data["current_period_from"].strftime("%Y-%m-%dT%H:%M") == "2024-05-19T20:00"
    assert data["current_period_to"].strftime("%Y-%m-%dT%H:%M") == "2024-05-19T20:30"
    assert data["current_period_forecast"] == 307
    assert data["current_period_national_index"] == "low"
    assert data["current_period_national_forecast"] == 145
    assert data["current_period_index"] == "high"
    assert data["lowest_period_from"].strftime("%Y-%m-%dT%H:%M") == "2024-05-20T14:00"
    assert data["lowest_period_to"].strftime("%Y-%m-%dT%H:%M") == "2024-05-20T14:30"
    assert data["lowest_period_forecast"] == 161
    assert data["lowest_period_index"] == "moderate"
    assert data["postcode"] == "BH1"
    assert data["current_low_carbon_percentage"] == 14.6
    assert data["optimal_window_forecast"] == 172
    assert data["optimal_window_index"] == "moderate"
    assert data["optimal_window_from"].strftime("%Y-%m-%dT%H:%M") == "2024-05-20T12:00"
    assert data["optimal_window_to"].strftime("%Y-%m-%dT%H:%M") == "2024-05-20T16:00"
    assert data["forecast"][0]["optimal"] == False
    # TODO: Add further tests for optimal window 48 hour predictions, expand testset to cover this. 

@pytest.mark.asyncio
async def test_request_data():
    client = Client("BH1")
    response = await client.async_get_data()
    print(response)
    data = response["data"]

    assert isinstance(data["current_period_from"], date)
    assert isinstance(data["current_period_to"], date)
    assert isinstance(data["current_period_forecast"], int)
    assert data["current_period_national_index"]  in ["very high", "moderate", "high", "low", "medium"]
    assert isinstance(data["current_period_national_forecast"], int)
    assert data["current_period_index"] in ["very high", "moderate", "high", "low", "medium"]
    assert isinstance(data["lowest_period_from"], date)
    assert isinstance(data["lowest_period_to"], date)
    assert isinstance(data["lowest_period_forecast"], int)
    assert data["lowest_period_index"] in ["very high", "moderate", "high", "low", "medium"]
    assert data["postcode"] == "BH1"
    assert isinstance(data["current_low_carbon_percentage"], float)
