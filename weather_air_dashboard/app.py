import os

import streamlit as st
from dotenv import load_dotenv

from weather_air_dashboard.api_clients.iqair import IQAirClient
from weather_air_dashboard.api_clients.openweather import OpenWeatherClient
from weather_air_dashboard.data_processing.analysis import process_forecast_data
from weather_air_dashboard.visualisation.plots import create_forecast_figure
from weather_air_dashboard.visualisation.ui_components import (
    display_air_quality,
    display_current_weather,
    display_forecast_section,
    display_map,
)

# CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Dashboard Météo", page_icon="🌦️", layout="wide")

# CHARGEMENT DES SECRETS
load_dotenv()


@st.cache_resource  # Cache la ressource (le client API)
def init_weather_client():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        st.error("Clé API OpenWeather manquante.")
        st.stop()
    return OpenWeatherClient(api_key=api_key)


@st.cache_resource
def init_air_client():
    api_key = os.getenv("IQAIR_API_KEY")
    if not api_key:
        st.error("Clé API IQAir manquante.")
        st.stop()
    return IQAirClient(api_key=api_key)


@st.cache_data(ttl="1h")  # Cache les données pour 1 heure
def get_all_data(city_name: str):
    weather_client = init_weather_client()
    air_client = init_air_client()

    weather_data = weather_client.get_current_weather(city_name)
    lat, lon = weather_data["coord"]["lat"], weather_data["coord"]["lon"]
    forecast_data = weather_client.get_forecast(lat=lat, lon=lon)
    air_quality_data = air_client.get_air_quality_by_coordinates(lat=lat, lon=lon)

    return weather_data, forecast_data, air_quality_data


# --- TITRE ---
st.title("Tableau de Bord Météo & Climat 🌦️")
st.markdown(
    "Un tableau de bord pour suivre la météo, " "les prévisions et la qualité de l'air."
)

weather_client = init_weather_client()
air_client = init_air_client()

# --- BARRE LATÉRALE ---
st.sidebar.header("Paramètres")
city = st.sidebar.text_input("Entrez le nom d'une ville :", "Paris")

# --- CORPS PRINCIPAL (ORCHESTRATEUR) ---
if st.sidebar.button("Rechercher"):
    if not city:
        st.warning("Veuillez entrer un nom de ville.")
        st.stop()

    try:
        with st.spinner(f"Recherche des données pour {city}..."):
            # Appels API
            weather_data, forecast_data, air_quality_data = get_all_data(city)
            st.success(f"Données pour {weather_data.get('name')} récupérées !")

        lat, lon = weather_data["coord"]["lat"], weather_data["coord"]["lon"]
        df_forecast = process_forecast_data(forecast_data)
        forecast_fig = create_forecast_figure(df_forecast)

        # Afficher les composants UI
        col1, col2 = st.columns([2, 1]) # Donne 2/3 de la place à la partie gauche
        
        with col1:
            with st.container(border=True):
                display_current_weather(weather_data)
            
            with st.container(border=True):
                display_air_quality(air_quality_data)

        with col2, st.container(border=True):
            # C'est ici qu'on appelle la fonction map !
            display_map(lat, lon) 

        st.divider()
        
        with st.container(border=True):
            display_forecast_section(forecast_fig, df_forecast)
            
    except Exception as e:
        st.error(f"Une erreur est survenue pour '{city}'. Détail: {e}")

else:
    st.info(
        "Veuillez entrer une ville et cliquer sur 'Rechercher' dans la barre latérale."
    )
