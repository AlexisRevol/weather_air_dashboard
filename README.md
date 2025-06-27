# Météo Dashboard

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Aperçu du Dashboard](https://raw.githubusercontent.com/AlexisRevol/weather_air_dashboard/main/.github/assets/demo_weather.gif)

Un tableau de bord interactif pour visualiser la météo en temps réel, les prévisions sur 5 jours et la qualité de l'air pour n'importe quelle ville dans le monde.

---


## Stack Technique

Ce projet met en œuvre une stack moderne de data science et de développement web en Python.

*   **Backend & Traitement de Données :**
    *   **Langage :** Python 3.11+
    *   **Manipulation de Données :** Pandas, NumPy
    *   **Requêtes API :** HTTpx

*   **Fournisseurs de Données (API) :**
    *   **OpenWeatherMap :** Pour les données météo actuelles et les prévisions.
    *   **IQAir :** Pour les données de qualité de l'air.
    *   **[Optionnel] Meteostat :** Pour les données climatiques historiques (fonctionnalité à venir).

*   **Frontend & Visualisation :**
    *   **Dashboard :** Streamlit
    *   **Graphiques :** Plotly Express
    *   **Cartographie :** Pydeck

*   **Outils de Développement (DevOps) :**
    *   **Gestion des Dépendances & Environnement :** Poetry
    *   **Qualité du Code (Linting & Formatting) :** Ruff
    *   **Tests :** Pytest

---

## Installation et Lancement Local

Pour lancer ce projet sur votre machine locale, suivez ces étapes.

### Prérequis

*   Python 3.11 ou supérieur
*   [Poetry](https://python-poetry.org/docs/#installation) installé sur votre machine.

### 1. Cloner le Dépôt

```bash
git clone https://github.com/AlexisRevol/weather_air_dashboard.git
cd weather_air_dashboard
```

### 2. Créer le fichier d'environnement

Vous aurez besoin de clés API gratuites pour OpenWeatherMap et IQAir.

* Créez un compte sur OpenWeatherMap et IQAir.
* À la racine du projet, créez un fichier nommé .env.
* Ajoutez-y vos clés API comme suit :

```bash
OPENWEATHER_API_KEY="cle_openweather"
IQAIR_API_KEY="cle_iqair"
```

### 3. Installer les dépendances

Poetry s'occupera de créer un environnement virtuel et d'installer tous les packages nécessaires.

```bash
poetry install
```

### 4. Lancer l'application Streamlit

Utilisez Poetry pour lancer le script de l'application.

```bash
poetry run python -m streamlit run weather_air_dashboard/app.py
```

L'application devrait s'ouvrir automatiquement dans votre navigateur à l'adresse http://localhost:8501.