import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import random
from matplotlib import style

style.use('seaborn-vibrant')

# Load data and models
df = pd.read_csv("weather_data.csv")
df['DATE'] = pd.to_datetime(df['DATE'])

with open("temp_model.pkl", "rb") as f:
    temp_model = pickle.load(f)
with open("rain_model.pkl", "rb") as f:
    rain_model = pickle.load(f)

def get_recent_lag_features(start_date=None):
    if start_date:
        recent = df[df['DATE'] < start_date].tail(7).copy()
    else:
        recent = df.tail(7).copy()
    features = {}
    for i in range(7):
        features[f'TAVG_lag_{i+1}'] = recent.iloc[-(i+1)]['TAVG'] if i < len(recent) else 60
        features[f'PRCP_lag_{i+1}'] = recent.iloc[-(i+1)]['PRCP'] if i < len(recent) else 0
    return pd.DataFrame([features])

def predict_weather(start_date=None):
    features = get_recent_lag_features(start_date)
    temp_f = temp_model.predict(features)[0]
    temp_c = (temp_f - 32) * 5 / 9
    rain_inch = rain_model.predict(features)[0]
    rain_percent = 1 if np.isnan(rain_inch) else min(max(round(rain_inch * 10, 2), 1), 100)
    if rain_percent == 0:
        rain_percent = random.randint(1, 5)
    return round(temp_c, 2), round(rain_percent, 2)

def plot_temp_trend(inquiry_date):
    is_future = inquiry_date > df['DATE'].max().date()

    base_date = inquiry_date if is_future else inquiry_date - timedelta(days=5)
    past_data = df[(df['DATE'].dt.date >= base_date) & (df['DATE'].dt.date <= inquiry_date)][['DATE', 'TAVG']].copy()
    past_data['Type'] = 'Past'
    past_data['Temp_C'] = (past_data['TAVG'] - 32) * 5 / 9

    future_preds = []
    if is_future:
        features = get_recent_lag_features(inquiry_date)
        for i in range(6):
            temp_f = temp_model.predict(features)[0]
            temp_c = (temp_f - 32) * 5 / 9
            future_date = inquiry_date + timedelta(days=i)
            future_preds.append({'DATE': future_date, 'Temp_C': temp_c, 'Type': 'Future'})
            for j in range(6, 0, -1):
                features[f'TAVG_lag_{j+1}'] = features[f'TAVG_lag_{j}']
            features['TAVG_lag_1'] = temp_f

    future_df = pd.DataFrame(future_preds)
    temp_plot_df = pd.concat([past_data[['DATE', 'Temp_C', 'Type']], future_df], ignore_index=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    for label, grp in temp_plot_df.groupby('Type'):
        ax.plot(grp['DATE'], grp['Temp_C'], marker='o', label=label)
    ax.axvline(x=inquiry_date, color='gray', linestyle='--', alpha=0.6)
    ax.set_title("Temperature Trend (Past & Future)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("Date")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Streamlit UI
st.title("🌦️ Weather Insight App")
st.write("Predict future and explore past weather details based on date.")

# Date input
inquiry_date = st.date_input("Select a date to view/predict weather:", value=datetime.today().date())

if inquiry_date <= df['DATE'].max().date():
    past_record = df[df['DATE'].dt.date == inquiry_date]
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
    temp_c, rain_percent = predict_weather(inquiry_date)
    st.metric("🌡️ Predicted Temperature (°C)", f"{temp_c} °C")
    st.metric("☔ Chance of Rain (%)", f"{rain_percent}%")

if st.button("📈 Show Temperature Trend"):
    plot_temp_trend(inquiry_date)
