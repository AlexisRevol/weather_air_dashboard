# weather_air_dashboard/app.py
"""
Point d'entrée principal de l'application Streamlit pour le tableau de bord Météo.
"""

import os

import streamlit as st
from dotenv import load_dotenv

# Imports des modules du projet, organisés par responsabilité
from weather_air_dashboard.api_clients.iqair import IQAirClient
from weather_air_dashboard.api_clients.openweather import OpenWeatherClient
from weather_air_dashboard.data_processing.analysis import (
    aggregate_daily_forecast,
    process_forecast_data,
)
from weather_air_dashboard.visualisation.plots import create_forecast_figure
from weather_air_dashboard.visualisation.ui_components import (
    display_air_quality,
    display_current_weather,
    display_forecast_section,
    display_map,
)

# Configuration de la Page
st.set_page_config(
    page_title="Dashboard Météo & Qualité de l'Air",
    page_icon="🌍",
    layout="wide",
)

# Chargement des Variables d'Environnement
load_dotenv()


# Initialisation des Services avec Caching


@st.cache_resource
def init_weather_client() -> OpenWeatherClient:
    """
    Initialise et met en cache le client API pour OpenWeatherMap.

    Utilise @st.cache_resource car le client est une ressource "lourde"
    qui ne doit être créée qu'une seule fois par session.

    Returns:
        OpenWeatherClient: Une instance du client API.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        st.error(
            "Clé API OpenWeather manquante. Veuillez la configurer dans les secrets."
        )
        st.stop()
    return OpenWeatherClient(api_key=api_key)


@st.cache_resource
def init_air_client() -> IQAirClient:
    """
    Initialise et met en cache le client API pour IQAir.

    Returns:
        IQAirClient: Une instance du client API.
    """
    api_key = os.getenv("IQAIR_API_KEY")
    if not api_key:
        st.error("Clé API IQAir manquante. Veuillez la configurer dans les secrets.")
        st.stop()
    return IQAirClient(api_key=api_key)


@st.cache_data(ttl="1h")
def get_all_data(city_name: str) -> tuple[dict, dict, dict]:
    """
    Récupère toutes les données (météo, prévisions, qualité de l'air)
    pour une ville donnée et met les résultats en cache.

    Utilise @st.cache_data car le résultat de cette fonction (les données)
    dépend de l'argument `city_name`. Les données sont mises en cache pour 1 heure.

    Args:
        city_name (str): Le nom de la ville à rechercher.

    Returns:
        tuple[dict, dict, dict]: Un tuple contenant les données météo,
                                 les prévisions et les données de qualité d'air.
    """
    weather_cli = init_weather_client()
    air_cli = init_air_client()

    weather_data = weather_cli.get_current_weather(city_name)
    lat, lon = weather_data["coord"]["lat"], weather_data["coord"]["lon"]
    forecast_data = weather_cli.get_forecast(lat=lat, lon=lon)
    air_quality_data = air_cli.get_air_quality_by_coordinates(lat=lat, lon=lon)

    return weather_data, forecast_data, air_quality_data


def main():
    """
    Fonction principale qui construit et exécute l'application Streamlit.
    """
    st.title("Tableau de Bord Météo & Climat 🌦️")
    st.markdown(
        "Un outil pour suivre la météo, les prévisions et la qualité d'air des villes."
    )

    # Barre Latérale pour les Entrées Utilisateur
    st.sidebar.header("Paramètres de Recherche")
    city = st.sidebar.text_input("Entrez le nom d'une ville", "Paris")

    if st.sidebar.button("Rechercher", type="primary"):
        if not city:
            st.warning("Veuillez entrer un nom de ville.")
            st.stop()

        try:
            # Récupération des données (via le cache)
            with st.spinner(f"Recherche des données pour {city}..."):
                weather_data, forecast_data, air_quality_data = get_all_data(city)

            st.success(f"Données pour **{weather_data.get('name')}** récupérées !")

            # Traitement et Préparation des données
            lat, lon = weather_data["coord"]["lat"], weather_data["coord"]["lon"]
            df_hourly = process_forecast_data(forecast_data)
            df_daily = aggregate_daily_forecast(df_hourly)
            forecast_fig = create_forecast_figure(df_hourly)

            # Affichage des Composants UI
            col1, col2 = st.columns([2, 1])

            with col1:
                with st.container(border=True):
                    display_current_weather(weather_data)
                with st.container(border=True):
                    display_air_quality(air_quality_data)

            with col2, st.container(border=True):
                display_map(lat, lon)

            st.divider()

            with st.container(border=True):
                display_forecast_section(forecast_fig, df_daily, df_hourly)

        except Exception as e:
            st.error(f"Une erreur est survenue lors de la recherche pour '{city}'.")
            st.error(f"Détail : {e}")
            with st.expander("Afficher les détails techniques de l'erreur"):
                st.exception(e)
    else:
        st.info("Veuillez entrer une ville et cliquer sur 'Rechercher' pour commencer.")


if __name__ == "__main__":
    main()
