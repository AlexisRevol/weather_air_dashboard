import pandas as pd
import streamlit as st
from plotly.graph_objects import Figure


def display_current_weather(weather_data: dict):
    """Affiche le bloc de la météo actuelle."""
    st.header(
        f"Météo actuelle à"
        f" {weather_data.get('name')}, {weather_data['sys']['country']}"
    )

    col1, col2, col3, col4 = st.columns(4)

    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    description = weather_data["weather"][0]["description"].capitalize()
    icon_code = weather_data["weather"][0]["icon"]
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    col1.metric("Température", f"{temp:.1f} °C")
    col2.metric("Ressenti", f"{feels_like:.1f} °C")
    col3.metric("Ciel", description)
    col4.image(icon_url, width=80)


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
