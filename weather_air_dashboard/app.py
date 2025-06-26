import os

import streamlit as st
from dotenv import load_dotenv

from weather_air_dashboard.api_clients.openweather import OpenWeatherClient

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
IQAIR_API_KEY = os.getenv("IQAIR_API_KEY")

st.title("Tableau de Bord Météo 🌦️")

if not OPENWEATHER_API_KEY:
    st.error(
        "La clé API OpenWeather n'a pas été trouvée."
        "Veuillez vérifier votre fichier .env."
    )
    st.stop()

try:
    client = OpenWeatherClient(api_key=OPENWEATHER_API_KEY)
except Exception as e:
    st.error(f"Erreur lors de l'initialisation du client API : {e}")
    st.stop()


# Interface utilisateur
city = st.text_input("Entrez le nom d'une ville :", "Paris")

if st.button("Rechercher"):
    if not city:
        st.warning("Veuillez entrer un nom de ville.")
    else:
        try:
            with st.spinner(f"Recherche de la météo pour {city}..."):
                weather_data = client.get_current_weather(city)

            st.success("Données récupérées !")
            st.subheader(f"Météo actuelle à {weather_data.get('name')}")

            # Affiche des infos simples et jolies
            col1, col2, col3 = st.columns(3)
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            description = weather_data["weather"][0]["description"].capitalize()

            col1.metric("Température", f"{temp:.1f} °C")
            col2.metric("Ressenti", f"{feels_like:.1f} °C")
            col3.metric("Ciel", description)

            # Pour le debug,afficher le JSON brut
            with st.expander("Voir les données brutes (JSON)"):
                st.json(weather_data)

        except Exception as e:
            st.error(
                f"Une erreur est survenue pour la ville '{city}'. "
                f"Veuillez vérifier le nom ou réessayez. Détail: {e}"
        )
