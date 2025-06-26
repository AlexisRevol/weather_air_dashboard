import pandas as pd


def process_forecast_data(forecast_data: dict) -> pd.DataFrame:
    """
    Traite les données brutes de prévisions de l'API OpenWeather
    et les transforme en un DataFrame Pandas
    """
    forecast_list = forecast_data["list"]
    df = pd.DataFrame(forecast_list)

    # Conversion du timestamp en datetime et extraction des données utiles
    df["dt_txt"] = pd.to_datetime(df["dt_txt"])
    df["temp"] = df["main"].apply(lambda x: x.get("temp"))
    df["feels_like"] = df["main"].apply(lambda x: x.get("feels_like"))
    df["weather_desc"] = df["weather"].apply(lambda x: x[0].get("description"))
    df["weather_icon"] = df["weather"].apply(lambda x: x[0].get("icon"))

    # Sélectionner et renommer les colonnes pour plus de clarté
    df_cleaned = df[
        ["dt_txt", "temp", "feels_like", "weather_desc", "weather_icon"]
    ].copy()
    df_cleaned.rename(
        columns={"dt_txt": "Date", "temp": "Température (°C)"}, inplace=True
    )

    return df_cleaned
