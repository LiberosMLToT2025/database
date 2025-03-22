from uagents import Agent, Context
import requests
import json
from datetime import datetime, timedelta
import os

# Tworzenie agenta
satellite_agent = Agent(
    name="nasa_satellite", 
    seed="nasa_satellite_seed", 
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]
)

# Konfiguracja API NASA dla Coronal Mass Ejection (CME) Analysis
NASA_API_KEY = "DEMO_KEY"  # Zamień na swój klucz API
NASA_CME_API_URL = "https://api.nasa.gov/DONKI/CMEAnalysis"

# Ścieżka do pliku JSON
DATA_FILE_PATH = "nasa_cme_data.json"

# Endpoint FastAPI do wysyłania danych
FASTAPI_ENDPOINT = "http://localhost:8000/upload"

@satellite_agent.on_interval(period=3600)  # Co godzinę
async def fetch_and_save_cme_data(ctx: Context):
    try:
        # Obliczanie dat (ostatnie 30 dni)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Formatowanie dat do formatu wymaganego przez API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Parametry zapytania do API NASA
        params = {
            "startDate": start_date_str,
            "endDate": end_date_str,
            "mostAccurateOnly": "true",
            "completeEntryOnly": "true",
            "speed": "0",
            "halfAngle": "0",
            "catalog": "ALL",
            "api_key": NASA_API_KEY
        }
        
        ctx.logger.info(f"Fetching CME data from NASA API for period: {start_date_str} to {end_date_str}")
        
        # Pobieranie danych z API NASA
        response = requests.get(NASA_CME_API_URL, params=params)
        
        if response.status_code == 200:
            cme_data = response.json()
            ctx.logger.info(f"Successfully fetched {len(cme_data)} CME records")
            
            # Przygotowanie danych do zapisania
            satellite_data = {
                "timestamp": datetime.now().isoformat(),
                "data_type": "CME_Analysis",
                "period": f"{start_date_str} to {end_date_str}",
                "data": cme_data
            }
            
            # Zapisywanie danych do pliku JSON
            with open(DATA_FILE_PATH, 'w') as json_file:
                json.dump(satellite_data, json_file, indent=2)
            
            ctx.logger.info(f"Data saved to {DATA_FILE_PATH}")
            
            # Wysyłanie pliku do FastAPI
            with open(DATA_FILE_PATH, 'rb') as file:
                files = {'file': (DATA_FILE_PATH, file, 'application/json')}
                ctx.logger.info(f"Sending file to {FASTAPI_ENDPOINT}")
                api_response = requests.post(FASTAPI_ENDPOINT, files=files)
                
                if api_response.status_code == 200:
                    ctx.logger.info("File successfully sent to the database")
                else:
                    ctx.logger.error(f"Failed to send file. Status code: {api_response.status_code}")
                    ctx.logger.error(f"Response: {api_response.text}")
        else:
            ctx.logger.error(f"Failed to fetch data from NASA API. Status code: {response.status_code}")
            ctx.logger.error(f"Response: {response.text}")
    
    except Exception as e:
        ctx.logger.error(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    satellite_agent.run()
