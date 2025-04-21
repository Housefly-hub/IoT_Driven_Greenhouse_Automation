import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime

# --- Load Models ---
with open("temp_model.pkl", "rb") as f:
    temp_model = pickle.load(f)

with open("rain_model.pkl", "rb") as f:
    rain_model = pickle.load(f)

# --- Load Data for Recent Lag Features ---
df = pd.read_csv("weather_data.csv")
df['DATE'] = pd.to_datetime(df['DATE'])
df = df.sort_values('DATE')

# Fill missing values
df[['PRCP', 'TMAX', 'TMIN']] = df[['PRCP', 'TMAX', 'TMIN']].fillna(method='ffill').fillna(method='bfill')
df['TAVG'] = df['TAVG'].fillna((df['TMAX'] + df['TMIN']) / 2)

# --- Function to Get Lag Features ---
def get_recent_lag_features():
    recent = df.tail(7).copy()
    features = {}

    for i in range(7):
        features[f'TAVG_lag_{i+1}'] = recent.iloc[-(i+1)]['TAVG']
        features[f'PRCP_lag_{i+1}'] = recent.iloc[-(i+1)]['PRCP']

    return pd.DataFrame([features])

# --- Streamlit UI ---
st.set_page_config(page_title="Weather Predictor", layout="centered")
st.title("🌤️ Weather Forecast App")
st.markdown("Predict **Average Temperature** and **Rainfall** for a future date using past weather trends.")

# Date Picker
selected_date = st.date_input("📅 Select a future date", min_value=datetime.now().date())

# Prediction Button
if st.button("Predict Weather"):
    try:
        today = df['DATE'].max().date()
        if selected_date <= today:
            st.warning("Please select a **future** date.")
        else:
            # Get lag features
            features = get_recent_lag_features()

            # Predict
            temp_f = temp_model.predict(features)[0]
            rain_inch = rain_model.predict(features)[0]

            # Convert units
            temp_c = (temp_f - 32) * 5 / 9
            rain_mm = rain_inch * 25.4

            # Display results
            st.success(f"📅 Prediction for {selected_date.strftime('%B %d, %Y')}:")
            st.metric("🌡️ Avg. Temperature", f"{temp_c:.2f} °C")
            st.metric("🌧️ Rainfall", f"{rain_mm:.2f} mm")

            # Rain description
            if rain_mm > 25:
                st.warning("☔ Heavy Rain Expected")
            elif rain_mm > 1:
                st.info("🌦️ Light Rain Possible")
            else:
                st.info("🌤️ Little or No Rain Expected")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
