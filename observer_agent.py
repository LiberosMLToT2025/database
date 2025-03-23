from uagents import Agent, Context, Model
import requests
import json
from datetime import datetime, timedelta

class IPSData(Model):
    catalogID: str
    location: str
    eventTime: str
    link: str
    
# Create the earth observer agent
earth_observer_agent = Agent(
    name="earth_observer",
    seed="earth_observer_seed",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"]
)

# NASA IPS API configuration
NASA_API_KEY = "DEMO_KEY"  # Replace with your API key
NASA_IPS_API_URL = "https://api.nasa.gov/DONKI/IPS"

# Satellite agent address to forward data
SATELLITE_AGENT_ADDRESS = "agent1q0s88rzrl6vx42fkn5j2rncsrc4vv8n507dcgvdduswa5gjpr2m6syhuwst"

@earth_observer_agent.on_interval(period=3600 * 24)  # Once per day
async def fetch_ips_data(ctx: Context):
    try:
        # Calculate dates (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Format dates for API (2025-02-21 to 2025-03-23 based on current date)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Parameters for NASA IPS API
        params = {
            "startDate": start_date_str,
            "endDate": end_date_str,
            "location": "ALL",
            "catalog": "ALL",
            "api_key": NASA_API_KEY
        }
        
        ctx.logger.info(f"Fetching Interplanetary Shock data from NASA API for period: {start_date_str} to {end_date_str}")
        
        try:
            # Make the actual API call
            response = requests.get(NASA_IPS_API_URL, params=params)
            
            if response.status_code == 200:
                ips_data = response.json()
                ctx.logger.info(f"Successfully fetched {len(ips_data)} IPS records")
                
                # Process each IPS event and send to satellite agent
                for ips_event in ips_data:
                    try:
                        # Extract relevant data from each IPS event
                        ips_message = IPSData(
                            catalogID=ips_event.get("catalogID", "Unknown"),
                            location=ips_event.get("location", "Unknown"),
                            eventTime=ips_event.get("eventTime", "Unknown"),
                            link=ips_event.get("link", "")
                        )
                        
                        # Send data to satellite agent
                        await ctx.send(SATELLITE_AGENT_ADDRESS, ips_message)
                        ctx.logger.info(f"Sent IPS event {ips_message.catalogID} to satellite agent")
                    except Exception as event_error:
                        ctx.logger.error(f"Error processing IPS event: {str(event_error)}")
                
            else:
                ctx.logger.error(f"Failed to fetch IPS data. Status code: {response.status_code}")
                ctx.logger.error(f"Response: {response.text}")
        
        except Exception as api_error:
            ctx.logger.error(f"API request error: {str(api_error)}")
        
    except Exception as e:
        ctx.logger.error(f"Error in fetch_ips_data: {str(e)}")

if __name__ == "__main__":
    earth_observer_agent.run()
