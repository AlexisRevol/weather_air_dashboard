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
