import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta

# Load models
with open("temp_model.pkl", "rb") as f:
    temp_model = pickle.load(f)

with open("rain_model.pkl", "rb") as f:
    rain_model = pickle.load(f)

# Load historical data to get recent lag features
df = pd.read_csv("weather_data.csv")
df['DATE'] = pd.to_datetime(df['DATE'])
df = df.sort_values('DATE')
df[['PRCP', 'TMAX', 'TMIN']] = df[['PRCP', 'TMAX', 'TMIN']].fillna(method='ffill').fillna(method='bfill')
df['TAVG'] = df['TAVG'].fillna((df['TMAX'] + df['TMIN']) / 2)

# Generate lag features (7 days) for latest date
def get_recent_lag_features():
    recent = df.tail(7).copy()
    features = {}

    for i in range(7):
        features[f'TAVG_lag_{i+1}'] = recent.iloc[-(i+1)]['TAVG']
        features[f'PRCP_lag_{i+1}'] = recent.iloc[-(i+1)]['PRCP']

    return pd.DataFrame([features])

# Streamlit UI
st.title("🌤️ Weather Predictor")
st.write("Enter a future date to predict average temperature and chance of rainfall.")

# Input
day = st.number_input("Day", min_value=1, max_value=31, value=1)
month = st.selectbox("Month", list(range(1, 13)))

if st.button("Predict"):
    try:
        today = df['DATE'].max()
        target_date = datetime(today.year + (1 if month < today.month or (month == today.month and day <= today.day) else 0), month, day)

        # Use latest available lag features
        features = get_recent_lag_features()

        # Predict
        temp_pred = temp_model.predict(features)[0]
        rain_pred = rain_model.predict(features)[0]

        # Output
        st.success(f"📅 Prediction for {target_date.strftime('%B %d')}:")
        st.metric("🌡️ Avg. Temperature (°C)", f"{temp_pred:.2f}")
        st.metric("🌧️ Expected Rainfall (mm)", f"{rain_pred:.2f}")
        if rain_pred > 1:
            st.warning("☔ Likely to Rain")
        else:
            st.info("🌤️ Less Chance of Rain")

    except Exception as e:
        st.error(f"Error: {str(e)}")
