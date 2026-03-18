import sqlite3
import pandas as pd
import fstring
from datetime import datetime, timedelta
from groq import Groq
import os
import tabulate

SQL_DB_PATH = "weather.db"
groq_key = os.environ.get("GROQ_API_KEY")

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
        Analyze the following weather data for tomorrow:

        {weather_table_text}

        Please provide a brief summary of the weather conditions for each city, 
        highlighting any extreme values or notable patterns.
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