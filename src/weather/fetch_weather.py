import requests
import pandas as pd

# Tiruppur coordinates
LATITUDE = 11.1085
LONGITUDE = 77.3411

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "daily": "precipitation_sum",
    "forecast_days": 10,
    "timezone": "auto"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()

    dates = data["daily"]["time"]
    rainfall = data["daily"]["precipitation_sum"]

    df = pd.DataFrame({
        "date": dates,
        "rainfall_mm": rainfall
    })

    print(df)

    df.to_csv("data/raw/weather_forecast.csv", index=False)
    print("Saved successfully.")

else:
    print("Error:", response.status_code)