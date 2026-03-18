import sqlite3
import pandas as pd
import fstring
from datetime import datetime, timedelta
from groq import Groq
import os
import tabulate

SQL_DB_PATH = "weather.db"
groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    raise ValueError("GROQ_API_KEY not found!")
# The poem should:

# compare the weather in the three locations
# describe the differences
# suggest where it would be nicest to be tomorrow
# be written in two languages
# Example idea: English + your native language

def view_weather_data():
    conn = sqlite3.connect(SQL_DB_PATH)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    query = f"SELECT * FROM weather WHERE date = '{tomorrow}'"
    
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    if df.empty:
        return "No weather data found in the database."

    weather_table_text = df.to_markdown(index=False)
    
    prompt = f"""
        You have to write a poem based on the data that comes from the weather forecast from tomorrow with this format:
        max_temp = max temperature in celcius
        precip = precipitation 
        max_wind = max wind
        avg_clouds = amount of clouds
        avg_humidity = how humid it will be

        the weather forecast with the last variables are in this table:

        {weather_table_text}

        Poem structure:
        write about the 2 weather variables with the higher difference
        write about where the day it would be nicer
        finally, write it in english and spanish
    """
    client = Groq(api_key=groq_key)
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": "You are a professional Poet that understand basic weather terminologies."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=1024
    )

    return completion.choices[0].message.content


if __name__ == "__main__":
    view_weather_data()