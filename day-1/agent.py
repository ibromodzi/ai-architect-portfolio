from google.adk.agents.llm_agent import Agent

# Mock tool implementation
# def get_current_time(city: str) -> dict:
#     """Returns the current time in a specified city."""
#     return {"status": "success", "city": city, "time": "10:30 AM"}


from datetime import datetime
import zoneinfo

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    city_timezones = {
        "ilorin": "Africa/Lagos",
        "lagos": "Africa/Lagos",
        "london": "Europe/London",
        "new york": "America/New_York",
        "tokyo": "Asia/Tokyo",
    }
    
    timezone_str = city_timezones.get(city.lower())
    
    if not timezone_str:
        return {"status": "error", "message": f"Timezone for '{city}' not found."}
    
    tz = zoneinfo.ZoneInfo(timezone_str)
    current_time = datetime.now(tz).strftime("%I:%M %p")
    
    return {"status": "success", "city": city, "time": current_time}



root_agent = Agent(
    model='gemini-flash-latest',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
)