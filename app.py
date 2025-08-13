
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random

# Page config
st.set_page_config(page_title="AI Climate Dashboard", layout="wide")

# Title & header
st.markdown("<h1 style='text-align: center; color: green;'>🌱 AI Climate Dashboard</h1>", unsafe_allow_html=True)
st.write("This free dashboard gives climate data, NDVI insights, and crop recommendations without any paid API keys.")

# Sidebar
st.sidebar.header("Settings")
location = st.sidebar.text_input("Enter location", "India")
view_mode = st.sidebar.radio("View Mode", ["Dashboard", "NDVI Data", "Crop Advice"])

# Simulated free weather data
def get_weather_data():
    days = pd.date_range(datetime.today(), periods=7)
    data = {
        "Date": days,
        "Temperature (°C)": [round(random.uniform(20, 35), 1) for _ in days],
        "Rainfall (mm)": [round(random.uniform(0, 20), 1) for _ in days],
        "Soil Moisture (%)": [round(random.uniform(10, 80), 1) for _ in days],
    }
    return pd.DataFrame(data)

weather_df = get_weather_data()

# Dashboard view
if view_mode == "Dashboard":
    st.subheader(f"📍 Climate Data for {location}")
    st.dataframe(weather_df, use_container_width=True)
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        fig_temp = px.line(weather_df, x="Date", y="Temperature (°C)", title="Temperature Trend")
        st.plotly_chart(fig_temp, use_container_width=True)
    with col2:
        fig_rain = px.bar(weather_df, x="Date", y="Rainfall (mm)", title="Rainfall")
        st.plotly_chart(fig_rain, use_container_width=True)

# NDVI Data view
elif view_mode == "NDVI Data":
    st.subheader("🛰 NDVI Data (Sample)")
    st.image("assets/ndvi_sample.png", caption="Sample NDVI image", use_column_width=True)
    st.write("This NDVI is a placeholder. Real NDVI data can be added from open satellite datasets.")

# Crop Advice view
elif view_mode == "Crop Advice":
    st.subheader("🌾 AI Crop Recommendations")
    avg_temp = weather_df["Temperature (°C)"].mean()
    avg_rain = weather_df["Rainfall (mm)"].mean()
    
    if avg_temp > 30 and avg_rain < 5:
        advice = "Plant drought-resistant crops like millet or sorghum."
    elif avg_temp < 25 and avg_rain > 10:
        advice = "Wheat, rice, and pulses will grow well."
    else:
        advice = "Maize, soybean, or mixed vegetables could work."
    
    st.success(f"Recommendation: {advice}")
