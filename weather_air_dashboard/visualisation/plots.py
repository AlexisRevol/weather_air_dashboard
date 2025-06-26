import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


def create_forecast_figure(df: pd.DataFrame) -> Figure:
    """
    Crée une figure Plotly pour l'évolution de la température à partir
    d'un DataFrame de prévisions.
    """
    fig = px.line(
        df,
        x="Date",
        y="Température (°C)",
        title="Évolution de la température",
        hover_name="weather_desc",
        markers=True,
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Température (°C)",
        title_x=0.5,
        legend_title_text="",
    )
    return fig
