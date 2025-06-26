import httpx


class IQAirClient:
    """Client pour interagir avec l'API IQAir."""

    BASE_URL = "http://api.airvisual.com/v2"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("La clé API IQAir est requise.")
        self.api_key = api_key
        self.http_client = httpx.Client()

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Méthode privée pour effectuer les requêtes."""
        params["key"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "success":
                raise Exception(
                    f"Erreur de l'API IQAir: {data.get('data', {}).get('message')}"
                )
            return data
        except httpx.HTTPStatusError as e:
            print(f"Erreur HTTP : {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Erreur de réseau : {e}")
            raise

    def get_air_quality_by_city(self, city: str, state: str, country: str) -> dict:
        """
        Récupère la qualité de l'air pour une ville, un état et un pays spécifiés.
        Ex: city="Paris", state="Ile-de-France", country="France"
        """
        params = {"city": city, "state": state, "country": country}
        return self._make_request("city", params=params)

    def get_air_quality_by_coordinates(self, lat: float, lon: float) -> dict:
        """
        Récupère la qualité de l'air pour des coordonnées géographiques.
        C'est souvent plus fiable que par nom de ville.
        """
        params = {"lat": str(lat), "lon": str(lon)}
        return self._make_request("nearest_city", params=params)
