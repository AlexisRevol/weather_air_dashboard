# weather_air_dashboard/app.py

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from weather_air_dashboard.api_clients.openweather import OpenWeatherClient

# CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Dashboard Météo",
    page_icon="🌦️",
    layout="wide" 
)

# CHARGEMENT DES SECRETS
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# TITRE DE L'APPLICATION
st.title("Tableau de Bord Météo & Climat 🌦️")
st.markdown(
    "Un tableau de bord pour suivre la météo, les prévisions et la qualité de l'air."
    )

if not OPENWEATHER_API_KEY:
    st.error(
        "La clé API OpenWeather n'a pas été trouvée."
        "Veuillez la définir dans votre fichier .env."
        )
    st.stop()  # Arrête l'exécution si la clé est manquante

# INITIALISATION DU CLIENT API
try:
    client = OpenWeatherClient(api_key=OPENWEATHER_API_KEY)
except Exception as e:
    st.error(f"Erreur lors de l'initialisation du client API : {e}")
    st.stop()

# BARRE LATÉRALE POUR LES INPUTS
st.sidebar.header("Paramètres")
city = st.sidebar.text_input("Entrez le nom d'une ville :", "Paris")


# CORPS PRINCIPAL DE L'APPLICATION
if st.sidebar.button("Rechercher"):
    if not city:
        st.warning("Veuillez entrer un nom de ville.")
        st.stop()

    try:
        # RÉCUPÉRATION DE LA MÉTÉO ACTUELLE
        with st.spinner(f"Recherche de la météo pour {city}..."):
            weather_data = client.get_current_weather(city)

        st.success(f"Données pour {weather_data.get('name')} récupérées !")
        
        st.header(f"Météo actuelle à "
                  f"{weather_data.get('name')}, {weather_data['sys']['country']}"
                  )

        # Affichage des métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        description = weather_data["weather"][0]["description"].capitalize()
        icon_code = weather_data["weather"][0]["icon"]
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

        col1.metric("Température", f"{temp:.1f} °C")
        col2.metric("Ressenti", f"{feels_like:.1f} °C")
        col3.metric("Ciel", description)
        col4.image(icon_url, width=80, caption="Icône")


        # RÉCUPÉRATION ET TRAITEMENT DES PRÉVISIONS
        coord = weather_data["coord"]
        lat, lon = coord["lat"], coord["lon"]

        with st.spinner("Récupération des prévisions sur 5 jours..."):
            forecast_data = client.get_forecast(lat=lat, lon=lon)
        
        # Traitement des données de prévision avec Pandas
        forecast_list = forecast_data["list"]
        df_forecast = pd.DataFrame(forecast_list)
        
        # Conversion du timestamp en datetime et extraction de la température
        df_forecast["dt_txt"] = pd.to_datetime(df_forecast["dt_txt"])
        df_forecast["temp"] = df_forecast["main"].apply(lambda x: x["temp"])
        df_forecast["weather_desc"] = df_forecast["weather"].apply(
            lambda x: x[0]['description']
            )


        # VISUALISATION DES PRÉVISIONS
        st.header("Prévisions sur 5 jours")
    
        fig = px.line(
            df_forecast, 
            x="dt_txt", 
            y="temp", 
            title="Évolution de la température",
            labels={"dt_txt": "Date et Heure", "temp": "Température (°C)"},
            hover_name="weather_desc",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Température (°C)",
            title_x=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

        # expander pour le débogage
        with st.expander("Voir les données brutes (JSON)"):
            st.subheader("Données météo actuelles")
            st.json(weather_data)
            st.subheader("Données de prévisions")
            st.json(forecast_data)

    except Exception as e:
        st.error(f"Une erreur est survenue lors de la recherche pour '{city}'.")
        st.error(f"Détail de l'erreur : {e}")

else:
    st.info(
        "Veuillez entrer une ville et cliquer sur 'Rechercher' dans la barre latérale."
        )