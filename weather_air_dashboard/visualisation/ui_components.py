import pandas as pd
import pydeck as pdk
import streamlit as st
from plotly.graph_objects import Figure


def display_current_weather(weather_data: dict):
    """Affiche le bloc de la météo actuelle de manière bien organisée."""

    city_name = weather_data.get("name")
    country = weather_data["sys"]["country"]
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
        st.image(icon_url, width=100)  # Icône plus visible
        st.metric("Humidité 💧", f"{humidity}%")


def display_forecast_section(
    fig: Figure, df_daily: pd.DataFrame, df_hourly: pd.DataFrame
):
    """Affiche la section complète des prévisions météo."""
    st.header("📅 Prévisions sur 5 jours")

    # --- Affichage du résumé journalier ---
    if not df_daily.empty:
        # Crée une colonne par jour
        cols = st.columns(len(df_daily))

        # On itère sur les colonnes et les lignes du DataFrame en même temps
        # C'est la manière la plus sûre et la plus propre de le faire
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

    # --- Affichage du graphique détaillé ---
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Voir les données de prévisions détaillées (par 3h)"):
        st.dataframe(df_hourly)


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
    """Affiche une carte 3D interactive pour la localisation."""
    st.header("📍 Localisation")

    initial_view_state = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=9,  # Un peu plus de zoom pour mieux voir la ville
        pitch=55,
    )

    location_layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame({"lat": [lat], "lon": [lon]}),
        get_position="[lon, lat]",
        get_color="[200, 30, 0, 160]",
        get_radius=1000,
        pickable=True,
    )

    map_style = "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"

    st.pydeck_chart(
        pdk.Deck(
            map_style=map_style,
            initial_view_state=initial_view_state,
            layers=[location_layer],
        )
    )
