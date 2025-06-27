# tests/test_api_clients.py

import httpx
import pytest

from weather_air_dashboard.api_clients.openweather import OpenWeatherClient


@pytest.fixture
def mock_httpx_client(mocker):
    mock = mocker.patch("httpx.Client", autospec=True)
    return mock.return_value

# Données de test
FAKE_API_KEY = "une-fausse-cle-api"
FAKE_URL = "https://api.openweathermap.org/data/2.5/weather"

SUCCESSFUL_WEATHER_RESPONSE = {
    "coord": {"lon": 2.3488, "lat": 48.8534},
    "weather": [{"id": 800, "main": "Clear", "description": "ciel dégagé", "icon": "01d"}],
    "main": {"temp": 20.0, "feels_like": 19.5, "humidity": 50},
    "wind": {"speed": 5.0},
    "name": "Paris",
    "sys": {"country": "FR"},
}

# Tests pour OpenWeatherClient

def test_openweather_client_initialization_requires_api_key():
    with pytest.raises(ValueError, match="La clé API est requise."):
        OpenWeatherClient(api_key="")

def test_get_current_weather_success(mock_httpx_client):
    """Teste un appel réussi à get_current_weather en utilisant un mock."""
    mock_request = httpx.Request("GET", FAKE_URL)
    mock_response = httpx.Response(
        200, 
        json=SUCCESSFUL_WEATHER_RESPONSE, 
        request=mock_request
    )
    mock_httpx_client.get.return_value = mock_response

    client = OpenWeatherClient(api_key=FAKE_API_KEY)
    weather_data = client.get_current_weather("Paris")

    mock_httpx_client.get.assert_called_once()
    call_args, call_kwargs = mock_httpx_client.get.call_args
    assert call_args[0] == FAKE_URL
    assert call_kwargs["params"]["q"] == "Paris"
    assert weather_data == SUCCESSFUL_WEATHER_RESPONSE

def test_get_current_weather_http_error(mock_httpx_client):
    """Teste la gestion d'une erreur HTTP (ex: 404 Not Found)."""
    mock_request = httpx.Request("GET", FAKE_URL)
    mock_response = httpx.Response(404, request=mock_request)
    

    http_error = httpx.HTTPStatusError(
        "Not Found", request=mock_request, response=mock_response
    )
    mock_httpx_client.get.side_effect = http_error

    client = OpenWeatherClient(api_key=FAKE_API_KEY)

    with pytest.raises(httpx.HTTPStatusError):
        client.get_current_weather("VilleInexistante")