# weather_air_dashboard/visualisation/ui_components.py
"""
Module contenant des "composants" pour construire l'interface utilisateur Streamlit.
"""

import pandas as pd
import pydeck as pdk
import streamlit as st
from plotly.graph_objects import Figure


def display_current_weather(weather_data: dict):
    """
    Affiche le bloc d'informations pour la météo actuelle.

    Args:
        weather_data (dict): Dictionnaire de données brutes provenant de
        l'API OpenWeather.
    """
    city_name = weather_data.get("name", "N/A")
    country = weather_data.get("sys", {}).get("country", "")
    st.header(f"☀️ Météo actuelle à {city_name}, {country}")

    col1, col2, col3 = st.columns(3)

    # Extraction et préparation des données ---
    main_data = weather_data.get("main", {})
    weather_info = weather_data.get("weather", [{}])[0]
    wind_data = weather_data.get("wind", {})

    temp = main_data.get("temp", "N/A")
    feels_like = main_data.get("feels_like", "N/A")
    humidity = main_data.get("humidity", "N/A")
    description = weather_info.get("description", "Non disponible").capitalize()
    icon_code = weather_info.get("icon", "01d")
    wind_speed_ms = wind_data.get("speed", 0)
    wind_speed_kmh = wind_speed_ms * 3.6

    # Colonne 1 : Températures
    with col1:
        st.metric(
            "Température", f"{temp}°C" if isinstance(temp, (int, float)) else temp
        )
        st.metric(
            "Ressenti",
            f"{feels_like}°C" if isinstance(feels_like, (int, float)) else feels_like,
        )

    # Colonne 2 : Ciel et Vent
    with col2:
        st.metric("Ciel", description)
        st.metric("Vent 💨", f"{wind_speed_kmh:.1f} km/h")

    # Colonne 3 : Icône et Humidité
    with col3:
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        st.image(icon_url, width=100)
        st.metric(
            "Humidité 💧",
            f"{humidity}%" if isinstance(humidity, (int, float)) else humidity,
        )


def display_forecast_section(
    fig: Figure, df_daily: pd.DataFrame, df_hourly: pd.DataFrame
):
    """
    Affiche la section complète des prévisions, incluant un résumé journalier
    et un graphique détaillé par tranches de 3 heures.

    Args:
        fig (Figure): La figure Plotly de l'évolution horaire.
        df_daily (pd.DataFrame): DataFrame contenant le résumé par jour.
        df_hourly (pd.DataFrame): DataFrame contenant les données détaillées par heure.
    """
    st.header("📅 Prévisions sur 5 jours")

    if not df_daily.empty:
        # Crée une colonne par jour
        cols = st.columns(len(df_daily))

        for col, (_, row) in zip(cols, df_daily.iterrows(), strict=False):
            with col:
                st.metric(
                    label=row["Date"].strftime("%a %d"),
                    value=f"{row['temp_max']:.0f}°/{row['temp_min']:.0f}°",
                )
                icon_url = (
                    f"https://openweathermap.org/img/wn/{row['weather_icon']}@2x.png"
                )
                st.image(icon_url, caption=f"{row['temp_max']:.0f}°C", width=60)

    st.divider()

    # Affichage du graphique détaillé
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Voir les données de prévisions détaillées (par 3h)"):
        st.dataframe(df_hourly)


def get_aqi_color_and_level(aqi: int) -> tuple[str, str]:
    """
    Retourne la couleur et le niveau de qualité de l'air en fonction de l'indice AQI.
    Cette fonction utilitaire aide à créer un affichage visuellement intuitif.

    Args:
        aqi (int): L'indice de qualité de l'air.

    Returns:
        tuple[str, str]: Un tuple contenant la couleur (nom ou code hex) et le niveau
        textuel.
    """
    if 0 <= aqi <= 50:
        return "green", "Bonne"
    if 51 <= aqi <= 100:
        return "#FFD700", "Modérée"
    if 101 <= aqi <= 150:
        return "orange", "Nocive pour les groupes sensibles"
    if 151 <= aqi <= 200:
        return "red", "Nocive"
    if 201 <= aqi <= 300:
        return "purple", "Très nocive"
    return "maroon", "Dangereuse"


def display_air_quality(air_quality_data: dict):
    """
    Affiche le bloc d'informations pour la qualité de l'air.

    Args:
        air_quality_data (dict): Dictionnaire de données brutes de l'API IQAir.
    """
    st.header("🌬️ Qualité de l'Air")

    current_pollution = (
        air_quality_data.get("data", {}).get("current", {}).get("pollution", {})
    )
    if not current_pollution or "aqius" not in current_pollution:
        st.info("Données de qualité de l'air non disponibles pour cette localisation.")
        return

    aqi = current_pollution.get("aqius")
    main_pollutant = current_pollution.get("mainus", "N/A")
    color, level = get_aqi_color_and_level(aqi)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Indice Qualité Air (AQI)",
            value=aqi,
            help=f"Niveau: {level}. Indice basé sur le standard US EPA.",
        )
    with col2:
        st.metric("Polluant Principal", main_pollutant.upper())

    # normalise sur une échelle pertinente (ex: 0-200).
    st.progress(min(aqi, 200) / 200)
    st.markdown(
        f"**Niveau de qualité de l'air :** <span style='color:{color};'>{level}</span>",
        unsafe_allow_html=True,
    )


def display_map(lat: float, lon: float):
    """
    Affiche une carte 3D interactive pour la localisation en utilisant Pydeck.

    Args:
        lat (float): La latitude du point à afficher.
        lon (float): La longitude du point à afficher.
    """
    st.header("📍 Localisation")

    initial_view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=9, pitch=55)

    location_layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame({"lat": [lat], "lon": [lon]}),
        get_position="[lon, lat]",
        get_color="[200, 30, 0, 160]",
        get_radius=1000,
        pickable=True,
    )

    # fond de carte open-source (CartoDB/OpenStreetMap)
    map_style = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"

    st.pydeck_chart(
        pdk.Deck(
            map_style=map_style,
            initial_view_state=initial_view_state,
            layers=[location_layer],
        )
    )
