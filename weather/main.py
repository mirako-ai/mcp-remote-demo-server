import os, sys
from fastmcp import FastMCP, Context
from typing import Annotated
from pydantic import Field
import httpx
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.auth_provider import AuthTokenAuthProvider


auth_token=os.getenv('AUTH_TOKEN')
mcp = FastMCP(name=__name__, auth=AuthTokenAuthProvider([auth_token]))


NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(client: httpx.AsyncClient, url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }

    try:
        response = await client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None
    

def format_alert(feature: dict) -> str:
    """Format an alert feature into a concise string."""
    props = feature["properties"]
    return (
        f"Event: {props.get('event', 'Unknown')}\n"
        f"Area: {props.get('areaDesc', 'Unknown')}\n"
        f"Severity: {props.get('severity', 'Unknown')}\n"
        f"Status: {props.get('status', 'Unknown')}\n"
        f"Headline: {props.get('headline', 'No headline')}\n"
        "---"
    )


@mcp.tool()
async def get_alerts(
    state: Annotated[str, Field(description="Two-letter state code (e.g. CA, NY)")],
    ctx: Context
) -> str:
    """Get weather alerts for a state"""
    # Convert state to uppercase to ensure consistent format
    state = state.upper()
    if len(state) != 2:
        raise ValueError("State must be a two-letter code (e.g. CA, NY)")

    async with httpx.AsyncClient() as client:
        alerts_url = f"{NWS_API_BASE}/alerts?area={state}"
        alerts_data = await make_nws_request(client, alerts_url)

        if not alerts_data:
            raise ValueError("Failed to retrieve alerts data")

        features = alerts_data.get("features", [])
        if not features:
            raise ValueError(f"No active alerts for {state}")

        # Format each alert into a concise string
        formatted_alerts = [format_alert(feature) for feature in features[:20]]  # only take the first 20 alerts
        alerts_text = f"Active alerts for {state}:\n\n" + "\n".join(formatted_alerts)

        return (alerts_text)


@mcp.tool()
async def get_forecast(
    latitude: Annotated[float, Field(description="Latitude of the location")],
    longitude: Annotated[float, Field(description="Longitude of the location")],
    ctx: Context
) -> str:
    """Get weather forecast for a location"""
    # Basic coordinate validation
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180.")

    async with httpx.AsyncClient() as client:
        # First get the grid point
        lat_str = f"{latitude}"
        lon_str = f"{longitude}"
        points_url = f"{NWS_API_BASE}/points/{lat_str},{lon_str}"
        points_data = await make_nws_request(client, points_url)

        if not points_data:
            raise ValueError(f"Failed to retrieve grid point data for coordinates: {latitude}, {longitude}. This location may not be supported by the NWS API (only US locations are supported).")

        # Extract forecast URL from the response
        properties = points_data.get("properties", {})
        forecast_url = properties.get("forecast")

        if not forecast_url:
            raise ValueError("Failed to get forecast URL from grid point data")

        # Get the forecast
        forecast_data = await make_nws_request(client, forecast_url)

        if not forecast_data:
            raise ValueError("Failed to retrieve forecast data")

        # Format the forecast periods
        periods = forecast_data.get("properties", {}).get("periods", [])
        if not periods:
            raise ValueError("No forecast periods available")

        # Format each period into a concise string
        formatted_forecast = []
        for period in periods:
            forecast_text = (
                f"{period.get('name', 'Unknown')}:\n"
                f"Temperature: {period.get('temperature', 'Unknown')}°{period.get('temperatureUnit', 'F')}\n"
                f"Wind: {period.get('windSpeed', 'Unknown')} {period.get('windDirection', '')}\n"
                f"{period.get('shortForecast', 'No forecast available')}\n"
                "---"
            )
            formatted_forecast.append(forecast_text)

        forecast_text = f"Forecast for {latitude}, {longitude}:\n\n" + "\n".join(formatted_forecast)

        return forecast_text
    

if __name__ == '__main__':
    mcp.run(transport="streamable-http", port=os.getenv("PORT", 8080))