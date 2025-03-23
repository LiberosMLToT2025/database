from uagents import Agent, Context
import json
from datetime import datetime
import os

# Import the IPSData model from observer_agent
from observer_agent import IPSData

# Create the satellite agent
satellite_agent = Agent(
    name="nasa_satellite", 
    seed="nasa_satellite_seed", 
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]
)

# File path for IPS data
IPS_DATA_FILE_PATH = "ips_observation_data.json"

# FastAPI endpoint
FASTAPI_ENDPOINT = "http://localhost:8000/upload"

@satellite_agent.on_message(model=IPSData)
async def process_ips_data(ctx: Context, sender: str, msg: IPSData):
    try:
        ctx.logger.info(f"Received IPS data from {sender}: {msg.catalogID}")
        
        # Extract the data we want to save
        ips_data = {
            "catalogID": msg.catalogID,
            "location": msg.location,
            "eventTime": msg.eventTime,
            "link": msg.link
        }
        
        # Add timestamp for our records
        processed_data = {
            "timestamp": datetime.now().isoformat(),
            "data_type": "Interplanetary_Shock",
            "ips_data": ips_data
        }
        
        # Save IPS data to JSON file
        with open(IPS_DATA_FILE_PATH, 'w') as json_file:
            json.dump(processed_data, json_file, indent=2)
        
        ctx.logger.info(f"IPS data saved to {IPS_DATA_FILE_PATH}")
        
        # Send file to FastAPI
        await send_file_to_api(ctx, IPS_DATA_FILE_PATH)
    
    except Exception as e:
        ctx.logger.error(f"Error processing IPS data: {str(e)}")

async def send_file_to_api(ctx: Context, file_path: str):
    try:
        # Send file to FastAPI
        with open(file_path, 'rb') as file:
            files = {'file': (file_path, file, 'application/json')}
            ctx.logger.info(f"Sending file {file_path} to {FASTAPI_ENDPOINT}")
            api_response = requests.post(FASTAPI_ENDPOINT, files=files)
            
            if api_response.status_code == 200:
                ctx.logger.info(f"File {file_path} successfully sent to the database")
            else:
                ctx.logger.error(f"Failed to send file. Status code: {api_response.status_code}")
                ctx.logger.error(f"Response: {api_response.text}")
    except Exception as e:
        ctx.logger.error(f"Error sending file to API: {str(e)}")

if __name__ == "__main__":
    satellite_agent.run()
