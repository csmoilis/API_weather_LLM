import requests
import sqlite3
from datetime import datetime, timedelta

SQL_DB_PATH = "weather.db"

def init_db():
    """Initializes the database schema using a context manager to handle commits."""
    with sqlite3.connect(SQL_DB_PATH) as conn:
        conn.execute("""
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

def get_daily_forecast(lat, lon, name, date_str):
    """Fetches weather data for a single location."""
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
        "start_date": date_str,
        "end_date": date_str
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()["daily"]
    
    return (
        name,
        date_str,
        data["temperature_2m_max"][0],
        data["precipitation_sum"][0],
        data["wind_speed_10m_max"][0],
        int(data["cloud_cover_mean"][0]),
        int(data["relative_humidity_2m_mean"][0])
    )

def main():
    locations = [
        {"name": "Punta Arenas, Chile", "lat": -53.1548, "lon": -70.9112},
        {"name": "Viña del Mar, Chile", "lat": -33.0245, "lon": -71.5518},
        {"name": "Aalborg, Denmark", "lat": 57.0488, "lon": 9.9217}
    ]

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    weather_records = [get_daily_forecast(loc["lat"], loc["lon"], loc["name"], tomorrow) for loc in locations]

    init_db()
    with sqlite3.connect(SQL_DB_PATH) as conn:
        conn.executemany("""
            INSERT INTO weather (location, date, max_temp, precip, max_wind, avg_clouds, avg_humidity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, weather_records)

if __name__ == "__main__":
    main()
