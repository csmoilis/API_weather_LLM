import requests
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import chromadb

SQL_DB_PATH = "weather.db"


#Create the SQLite database and the weather table
def init_db():
    conn = sqlite3.connect(SQL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            date TEXT,
            max_temp REAL,
            precip REAL,
            max_wind REAL,
            avg_clouds INTEGER,
            avg_humidity INTEGER
        )
    """)
    conn.commit()
    return conn

def get_daily_forecast(lat, lon, name):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max", 
            "precipitation_sum", 
            "wind_speed_10m_max", 
            "cloud_cover_mean", 
            "relative_humidity_2m_mean"
        ],
        "timezone": "auto",
        "start_date": tomorrow,
        "end_date": tomorrow
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()["daily"]
    
    return (
        name,
        tomorrow,
        data["temperature_2m_max"][0],
        data["precipitation_sum"][0],
        data["wind_speed_10m_max"][0],
        int(data["cloud_cover_mean"][0]),
        int(data["relative_humidity_2m_mean"][0])
    )

locations = [
    {"name": "Punta Arenas, Chile", "lat": -53.1548, "lon": -70.9112},
    {"name": "Viña del Mar, Chile", "lat": -33.0245, "lon": -71.5518},
    {"name": "Aalborg, Denmark", "lat": 57.0488, "lon": 9.9217}
]

weather_records = [get_daily_forecast(loc["lat"], loc["lon"], loc["name"]) for loc in locations]

conn = init_db()
cursor = conn.cursor()
cursor.executemany("""
    INSERT INTO weather (location, date, max_temp, precip, max_wind, avg_clouds, avg_humidity)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", weather_records)

conn.commit()
conn.close()