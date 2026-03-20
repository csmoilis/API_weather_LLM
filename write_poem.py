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

def update_web_page(poem_content, weather_df):
    # Ensure the docs folder exists (required for GitHub Pages)
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
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; padding: 40px; max-width: 800px; margin: auto; background-color: #f4f7f6; }}
            .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            pre {{ white-space: pre-wrap; font-size: 1.1rem; color: #34495e; font-style: italic; }}
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
            {weather_df.to_html(index=False)}
        </div>
        <p style="text-align:center; font-size: 0.8rem;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </body>
    </html>
    """
    
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    result = generate_weather_poem()
    update_web_page(result, df)