import os

import streamlit as st
from dotenv import load_dotenv

from weather_air_dashboard.api_clients.openweather import OpenWeatherClient
from weather_air_dashboard.data_processing.analysis import process_forecast_data
from weather_air_dashboard.visualisation.plots import create_forecast_figure
from weather_air_dashboard.visualisation.ui_components import (
    display_current_weather,
    display_forecast_section,
)

# CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Dashboard Météo", page_icon="🌦️", layout="wide")

# CHARGEMENT DES SECRETS
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# --- TITRE ---
st.title("Tableau de Bord Météo & Climat 🌦️")
st.markdown(
    "Un tableau de bord pour suivre la météo, " "les prévisions et la qualité de l'air."
)

# --- VALIDATION ET INITIALISATION ---
if not OPENWEATHER_API_KEY:
    st.error("Clé API OpenWeather manquante. Vérifiez votre fichier .env.")
    st.stop()
try:
    client = OpenWeatherClient(api_key=OPENWEATHER_API_KEY)
except Exception as e:
    st.error(f"Erreur d'initialisation du client API : {e}")
    st.stop()

# --- BARRE LATÉRALE ---
st.sidebar.header("Paramètres")
city = st.sidebar.text_input("Entrez le nom d'une ville :", "Paris")

# --- CORPS PRINCIPAL (ORCHESTRATEUR) ---
if st.sidebar.button("Rechercher"):
    if not city:
        st.warning("Veuillez entrer un nom de ville.")
        st.stop()

    try:
        # 1. Obtenir les données brutes
        with st.spinner(f"Recherche des données pour {city}..."):
            weather_data = client.get_current_weather(city)
            lat, lon = weather_data["coord"]["lat"], weather_data["coord"]["lon"]
            forecast_data = client.get_forecast(lat=lat, lon=lon)
        st.success(f"Données pour {weather_data.get('name')} récupérées !")

        # 2. Traiter les données
        df_forecast = process_forecast_data(forecast_data)

        # 3. Créer les objets de visualisation
        forecast_fig = create_forecast_figure(df_forecast)

        # 4. Afficher les composants UI
        display_current_weather(weather_data)
        display_forecast_section(forecast_fig, df_forecast)

    except Exception as e:
        st.error(f"Une erreur est survenue pour '{city}'. Détail: {e}")

else:
    st.info(
        "Veuillez entrer une ville et cliquer sur"
        " 'Rechercher' dans la barre latérale."
    )
