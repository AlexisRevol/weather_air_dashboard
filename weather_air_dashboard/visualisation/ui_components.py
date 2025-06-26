import pandas as pd
import streamlit as st
from plotly.graph_objects import Figure


def display_current_weather(weather_data: dict):
    """Affiche le bloc de la météo actuelle de manière bien organisée."""
    
    city_name = weather_data.get('name')
    country = weather_data['sys']['country']
    st.header(f"Météo actuelle à {city_name}, {country}")

    # On utilise 3 colonnes pour bien espacer les infos
    col1, col2, col3 = st.columns(3)

    # --- Données extraites de l'API ---
    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    description = weather_data["weather"][0]["description"].capitalize()
    icon_code = weather_data["weather"][0]["icon"]
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    humidity = weather_data["main"]["humidity"]
    wind_speed_ms = weather_data["wind"]["speed"]
    wind_speed_kmh = wind_speed_ms * 3.6

    # --- Colonne 1 : Températures ---
    with col1:
        st.metric("Température", f"{temp:.1f} °C")
        st.metric("Ressenti", f"{feels_like:.1f} °C")

    # --- Colonne 2 : Ciel et Vent ---
    with col2:
        st.metric("Ciel", description)
        st.metric("Vent 💨", f"{wind_speed_kmh:.1f} km/h")

    # --- Colonne 3 : Icône et Humidité ---
    with col3:
        st.image(icon_url, width=100) # Icône plus visible
        st.metric("Humidité 💧", f"{humidity}%")

def display_forecast_section(fig: Figure, df: pd.DataFrame):
    """Affiche la section des prévisions météo."""
    st.header("Prévisions sur 5 jours")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Voir les données de prévisions détaillées"):
        st.dataframe(df)


def get_aqi_color_and_level(aqi: int) -> tuple[str, str]:
    """Retourne la couleur et le niveau de pollution en fonction de
    l'indice AQI (US).
    """
    if 0 <= aqi <= 50:
        return "green", "Bonne"
    elif 51 <= aqi <= 100:
        return "orange", "Modérée"
    elif 101 <= aqi <= 150:
        return "orange", "Nocive pour les groupes sensibles"
    elif 151 <= aqi <= 200:
        return "red", "Nocive"
    elif 201 <= aqi <= 300:
        return "red", "Très nocive"
    else:
        return "maroon", "Dangereuse"


def display_air_quality(air_quality_data: dict):
    """Affiche le bloc de la qualité de l'air."""
    st.header("Qualité de l'Air")

    current_pollution = (
        air_quality_data.get("data", {}).get("current", {}).get("pollution", {})
    )
    if not current_pollution:
        st.warning("Données de qualité de l'air non disponibles pour ce lieu.")
        return

    aqi = current_pollution.get("aqius")  # Indice AQI standard US
    main_pollutant = current_pollution.get("mainus")  # Polluant principal

    color, level = get_aqi_color_and_level(aqi)

    col1, col2 = st.columns(2)

    col1.metric(
        label="Indice de Qualité de l'Air (AQI)",
        value=aqi,
        help=f"Niveau: {level}. Un indice plus bas est meilleur.",
    )
    col2.metric("Polluant principal", main_pollutant.upper())

    # Barre de progression colorée pour l'AQI
    st.progress(value=min(aqi, 200) / 200)
    st.markdown(
        f"**Niveau de qualité de l'air : "
        f"<span style='color:{color};'>{level}</span>**",
        unsafe_allow_html=True,
    )


def display_map(lat: float, lon: float):
    """Affiche une carte centrée sur les coordonnées données."""
    st.header("Localisation")
    # st.map requiert un DataFrame avec les colonnes 'lat' et 'lon'
    map_data = pd.DataFrame({"lat": [lat], "lon": [lon]})
    st.map(map_data, zoom=10)
