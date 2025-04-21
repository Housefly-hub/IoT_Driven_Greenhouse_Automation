import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import random

# Load data and models
df = pd.read_csv("weather_data.csv")
df['DATE'] = pd.to_datetime(df['DATE'])

with open("temp_model.pkl", "rb") as f:
    temp_model = pickle.load(f)
with open("rain_model.pkl", "rb") as f:
    rain_model = pickle.load(f)

def get_recent_lag_features():
    recent = df.tail(7).copy()
    features = {}
    for i in range(7):
        features[f'TAVG_lag_{i+1}'] = recent.iloc[-(i+1)]['TAVG']
        features[f'PRCP_lag_{i+1}'] = recent.iloc[-(i+1)]['PRCP']
    return pd.DataFrame([features])

def predict_weather():
    features = get_recent_lag_features()
    temp_f = temp_model.predict(features)[0]
    temp_c = (temp_f - 32) * 5 / 9
    rain_inch = rain_model.predict(features)[0]
    rain_percent = 1 if np.isnan(rain_inch) else min(max(round(rain_inch * 10, 2), 1), 100)
    if rain_percent == 0:
        rain_percent = random.randint(1, 5)
    return round(temp_c, 2), round(rain_percent, 2)

def plot_temp_trend():
    past_5 = df.tail(5)[['DATE', 'TAVG']].copy()
    past_5['Type'] = 'Past'
    past_5['Temp_C'] = (past_5['TAVG'] - 32) * 5 / 9

    future_preds = []
    features = get_recent_lag_features()
    for i in range(5):
        temp_f = temp_model.predict(features)[0]
        temp_c = (temp_f - 32) * 5 / 9
        future_date = df['DATE'].max() + pd.Timedelta(days=i+1)
        future_preds.append({'DATE': future_date, 'Temp_C': temp_c, 'Type': 'Future'})
        for j in range(6, 0, -1):
            features[f'TAVG_lag_{j+1}'] = features[f'TAVG_lag_{j}']
        features['TAVG_lag_1'] = temp_f

    future_df = pd.DataFrame(future_preds)
    temp_plot_df = pd.concat([past_5[['DATE', 'Temp_C', 'Type']], future_df], ignore_index=True)

    fig, ax = plt.subplots(figsize=(10, 4))
    for label, grp in temp_plot_df.groupby('Type'):
        ax.plot(grp['DATE'], grp['Temp_C'], marker='o', label=label)
    ax.axvline(x=datetime.now(), color='gray', linestyle='--', alpha=0.6)
    ax.set_title("Past 5 Days and Predicted 5 Days Avg Temperature (°C)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("Date")
    ax.grid(True)
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Streamlit UI
st.title("🌦️ Weather Prediction App")
st.write("Predict future temperature and chance of rain based on past data.")

# Date selection
date_input = st.date_input("Select a date to view/predict weather:", min_value=df['DATE'].min().date(), max_value=(df['DATE'].max() + timedelta(days=5)).date())

if date_input <= df['DATE'].max().date():
    # Show past temperature
    past_record = df[df['DATE'].dt.date == date_input]
    if not past_record.empty:
        temp_c = (past_record['TAVG'].values[0] - 32) * 5 / 9
        rain_val = past_record['PRCP'].values[0]
        rain_percent = 1 if np.isnan(rain_val) else min(max(round(rain_val * 10, 2), 1), 100)
        if rain_percent == 0:
            rain_percent = random.randint(1, 5)
        st.metric("📅 Past Temperature (°C)", f"{round(temp_c, 2)} °C")
        st.metric("🌧️ Chance of Rain (%)", f"{rain_percent}%")
    else:
        st.warning("No data available for selected date.")
else:
    # Predict future weather
    temp_c, rain_percent = predict_weather()
    st.metric("🌡️ Predicted Temperature (°C)", f"{temp_c} °C")
    st.metric("☔ Chance of Rain (%)", f"{rain_percent}%")
    plot_temp_trend()
