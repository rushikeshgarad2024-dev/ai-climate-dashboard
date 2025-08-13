# app.py
# ----------------------------
# AI Climate Dashboard – 100% Free
# - Weather: Open-Meteo (no key)
# - NDVI: NASA GIBS (public), with local fallback at assets/ndvi_sample.png
# - Map: Folium / OpenStreetMap
# ----------------------------

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image
import os

st.set_page_config(page_title="AI Climate Dashboard", layout="wide")
st.title("🌍 AI Climate Dashboard – Free & Open Source")

st.write(
    "This AI dashboard predicts weather trends, assesses vegetation health (NDVI), "
    "and gives planting advice — all without paid APIs."
)

# ----------------------------
# Sidebar: Location & Settings
# ----------------------------
st.sidebar.header("📍 Location Settings")
lat = st.sidebar.number_input("Latitude", value=28.6139, help="Example: New Delhi ≈ 28.6139")
lon = st.sidebar.number_input("Longitude", value=77.2090, help="Example: New Delhi ≈ 77.2090")
days_ahead = st.sidebar.slider("Forecast Days", 7, 60, 30)

# ----------------------------
# Weather Forecast (Open-Meteo)
# ----------------------------
st.header("📊 Weather Forecast")

@st.cache_data(show_spinner=False, ttl=60 * 60)
def get_weather(lat: float, lon: float, days: int) -> pd.DataFrame | None:
    # Open-Meteo free endpoint, no API key needed
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
        f"&forecast_days={days}"
    )
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        dates = pd.to_datetime(data["daily"]["time"])
        tmax = data["daily"]["temperature_2m_max"]
        tmin = data["daily"]["temperature_2m_min"]
        rain = data["daily"]["precipitation_sum"]
        return pd.DataFrame(
            {
                "Date": dates,
                "Max Temp (°C)": tmax,
                "Min Temp (°C)": tmin,
                "Rainfall (mm)": rain,
            }
        )
    except Exception:
        return None

df_weather = get_weather(lat, lon, days_ahead)

if df_weather is not None and not df_weather.empty:
    st.line_chart(df_weather.set_index("Date")[["Max Temp (°C)", "Min Temp (°C)"]])
    st.bar_chart(df_weather.set_index("Date")[["Rainfall (mm)"]])
    with st.expander("Show raw weather table"):
        st.dataframe(df_weather, use_container_width=True)
else:
    st.error("Weather data not available right now. Try a different location or later.")

# ----------------------------
# NDVI Vegetation Health (NASA GIBS) with Fallback
# ----------------------------
st.header("🌱 Vegetation Health (NDVI)")

st.write(
    "We fetch an **NDVI** (Normalized Difference Vegetation Index) tile from NASA GIBS. "
    "If the live tile is temporarily unavailable, we show a local sample image so your app never looks empty."
)

@st.cache_data(show_spinner=False, ttl=60 * 60)
def get_ndvi_image(lat: float, lon: float) -> Image.Image | None:
    """Attempts to download a single NDVI tile from NASA GIBS (public, no key).
    If it fails, return None (the caller will use the local fallback).
    Note: Tile math is approximate and intended as a simple demo.
    """
    try:
        # Very rough tile math for the GoogleMapsCompatible_Level9 grid
        x = int((lon + 180) / 0.703125)
        y = int((90 - lat) / 0.703125)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        ndvi_url = (
            "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
            f"MODIS_Terra_NDVI_8Day/default/{date_str}/GoogleMapsCompatible_Level9/{x}/{y}/0.png"
        )
        r = requests.get(ndvi_url, timeout=15)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except Exception:
        return None

# Try live NDVI
ndvi_img = get_ndvi_image(lat, lon)

# Local fallback path (make sure this file exists in your repo)
FALLBACK_PATH = os.path.join("assets", "ndvi_sample.png")

if ndvi_img is not None:
    st.image(ndvi_img, caption="NDVI (NASA GIBS live tile)", use_container_width=True)
elif os.path.exists(FALLBACK_PATH):
    st.image(FALLBACK_PATH, caption="NDVI (Local sample fallback)", use_container_width=True)
    st.info(
        "Showing a **local sample** because the live NASA tile couldn't be fetched right now. "
        "Your app remains fully functional and demo-ready."
    )
else:
    st.warning(
        "NDVI image unavailable and no local fallback found. "
        "Add a sample image at `assets/ndvi_sample.png` to always have a visual."
    )

# ----------------------------
# Simple AI-style Planting Advice (Rule-based, free)
# ----------------------------
st.header("💡 Planting Advice (Rule-based)")

if df_weather is not None and not df_weather.empty:
    avg_tmax = float(np.mean(df_weather["Max Temp (°C)"]))
    avg_tmin = float(np.mean(df_weather["Min Temp (°C)"]))
    avg_rain = float(np.mean(df_weather["Rainfall (mm)"]))

    st.write(
        f"**Avg Max Temp:** {avg_tmax:.1f} °C  |  "
        f"**Avg Min Temp:** {avg_tmin:.1f} °C  |  "
        f"**Avg Rainfall:** {avg_rain:.1f} mm"
    )

    # Very simple, transparent rules (no paid model calls)
    if avg_tmax >= 26 and avg_rain >= 60:
        st.success("✅ Warm & wet: consider **rice, sugarcane, maize**.")
    elif avg_tmax <= 22 and avg_rain <= 30:
        st.info("🌾 Cooler & drier: consider **wheat, barley, chickpea**.")
    elif avg_rain < 20:
        st.warning("⚠ Low rainfall: consider **millet, sorghum, pigeon pea** (drought-tolerant).")
    else:
        st.write("🔎 Mixed conditions: consider **diverse cropping** and short-duration varieties.")
else:
    st.info("Weather data needed for planting advice.")

# ----------------------------
# Map View
# ----------------------------
st.header("🗺 Location Map")
m = folium.Map(location=[lat, lon], zoom_start=6, control_scale=True)
folium.Marker([lat, lon], tooltip="Selected Location").add_to(m)
st_folium(m, width=800, height=450)

st.caption("Data sources: Open-Meteo, NASA GIBS, OpenStreetMap — all free.")
