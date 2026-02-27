import requests

# Get weather for Tiruppur, India
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 11.1085,
    "longitude": 77.3411,
    "current_weather": True
}

response = requests.get(url, params=params)
data = response.json()
print(data["current_weather"])