import httpx


class OpenWeatherClient:
    """Client pour interagir avec l'API OpenWeatherMap."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("La clé API est requise.")
        self.api_key = api_key
        self.http_client = httpx.Client()

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Méthode privée pour effectuer les requêtes."""
        params["appid"] = self.api_key
        params["units"] = "metric"
        params["lang"] = "fr"

        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.http_client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Erreur HTTP : {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Erreur de réseau : {e}")
            raise

    def get_current_weather(self, city: str) -> dict:
        """Récupère la météo actuelle pour une ville."""
        return self._make_request("weather", params={"q": city})

    def get_forecast(self, lat: float, lon: float) -> dict:
        """Récupère les prévisions sur 5 jours / par tranches de 3 heures."""
        return self._make_request("forecast", params={"lat": lat, "lon": lon})
