import sqlite3
import pandas as pd
import requests
from datetime import datetime, timedelta
from groq import Groq
import os
import tabulate


SQL_DB_PATH = "weather.db"
groq_key = os.environ.get("GROQ_API_KEY")

def get_weather_and_poem():
    print("🚀 Starting write_poem.py...")
    conn = sqlite3.connect(SQL_DB_PATH)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"📅 Looking for database records for date: {tomorrow}")
    
    query = f"SELECT * FROM weather WHERE date = '{tomorrow}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("🚨 WARNING: The database returned 0 rows! Skipping poem generation.")
        return None, None

    print(f"✅ Found {len(df)} rows. Cleaning up duplicates...")
    
    df = df.drop_duplicates(subset=['location'], keep='last')
    
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    print("✍️ Requesting poem from AI...")

    weather_table_text = df.to_markdown(index=False)
    
    prompt = f"""
        Analyze the following weather data for tomorrow:
        {weather_table_text}

        Poem Requirements:
        1. Compare the three locations.
        2. Describe the differences in weather variables.
        3. Suggest where it would be nicest to be tomorrow.
        4. Write the poem in both English and Spanish.
    """
    
    client = Groq(api_key=groq_key)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional Poet that understands weather terminologies."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )

    return completion.choices[0].message.content, df

def update_web_page(poem_content, weather_df):
    if not os.path.exists('docs'):
        os.makedirs('docs')
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Weather Poem</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; line-height: 1.6; padding: 40px; max-width: 800px; margin: auto; background-color: #f4f7f6; }}
            .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            pre {{ white-space: pre-wrap; font-size: 1.1rem; color: #34495e; font-style: italic; background: #fafafa; padding: 15px; border-radius: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
        </style>
    </head>
    <body>
        <h1>Weather Forecast & Poem</h1>
        <div class="card">
            <h2>The Daily Poem</h2>
            <pre>{poem_content}</pre>
        </div>
        <div class="card">
            <h2>Weather Data</h2>
            {weather_df.to_html(index=False, classes='weather-table')}
        </div>
        <p style="text-align:center; font-size: 0.8rem;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </body>
    </html>
    """
    
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    poem, data_df = get_weather_and_poem()
    if poem and data_df is not None:
        update_web_page(poem, data_df)
    else:
        print("No data found to process.")
