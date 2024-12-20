from flask import Flask, request
from typing import Any, List
import httpx
import os

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

app = Flask(__name__)


def check_auth(request):
    if not request.authorization or not request.authorization.token == os.getenv('AUTH_TOKEN'):
        raise PermissionError("Invalid token")


@app.route("/list_tools")
def list_tools():
    check_auth(request)
    return [
        {
            "name": "get-alerts",
            "description": "Get weather alerts for a state",
            "parameters": {
                "properties": {
                    "state": {
                        "title": "state",
                        "type": "string",
                        "description": "Two-letter state code (e.g. CA, NY)"
                    },
                },
                "required": ["state"],
                "type": "object",
            },
        },
        {
            "name": "get-forecast",
            "description": "Get weather forecast for a location",
            "parameters": {
                "properties": {
                    "latitude": {
                        "title": "latitude",
                        "type": "number",
                        "description": "Latitude of the location"
                    },
                    "longitude": {
                        "title": "longitude",
                        "type": "number",
                        "description": "Longitude of the location"
                    },
                },
                "required": ["latitude", "longitude"],
                "type": "object",
            },
        }
    ]


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


def message_response(message: str):
    return {
        "status": "success",
        "message": message
    }


def custom_response(message: str, custom: dict):
    response = message_response(message)
    response.update(custom)
    return response


def error_response(error: str):
    return {
        "status": "failed",
        "message": error
    }


@app.route("/call_tool", methods=['POST'])
async def call_tool():
    check_auth(request)
    request_json = request.json
    name = request_json["name"]
    arguments = request_json["arguments"]
    profile = request_json["profile"] # profile.id and profile.metis_id will be provided

    if not arguments:
        raise error_response("Missing arguments")

    if name == "get-alerts":
        state = arguments.get("state")
        if not state:
            raise error_response("Missing state parameter")

        # Convert state to uppercase to ensure consistent format
        state = state.upper()
        if len(state) != 2:
            raise error_response("State must be a two-letter code (e.g. CA, NY)")

        async with httpx.AsyncClient() as client:
            alerts_url = f"{NWS_API_BASE}/alerts?area={state}"
            alerts_data = await make_nws_request(client, alerts_url)

            if not alerts_data:
                return error_response("Failed to retrieve alerts data")

            features = alerts_data.get("features", [])
            if not features:
                return error_response(f"No active alerts for {state}")

            # Format each alert into a concise string
            formatted_alerts = [format_alert(feature) for feature in features[:20]]  # only take the first 20 alerts
            alerts_text = f"Active alerts for {state}:\n\n" + "\n".join(formatted_alerts)

            return error_response(alerts_text)
    elif name == "get-forecast":
        try:
            latitude = float(arguments.get("latitude"))
            longitude = float(arguments.get("longitude"))
        except (TypeError, ValueError):
            return error_response("Invalid coordinates. Please provide valid numbers for latitude and longitude.")

        # Basic coordinate validation
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return error_response("Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180.")

        async with httpx.AsyncClient() as client:
            # First get the grid point
            lat_str = f"{latitude}"
            lon_str = f"{longitude}"
            points_url = f"{NWS_API_BASE}/points/{lat_str},{lon_str}"
            points_data = await make_nws_request(client, points_url)

            if not points_data:
                return error_response(f"Failed to retrieve grid point data for coordinates: {latitude}, {longitude}. This location may not be supported by the NWS API (only US locations are supported).")

            # Extract forecast URL from the response
            properties = points_data.get("properties", {})
            forecast_url = properties.get("forecast")

            if not forecast_url:
                return error_response("Failed to get forecast URL from grid point data")

            # Get the forecast
            forecast_data = await make_nws_request(client, forecast_url)

            if not forecast_data:
                return error_response("Failed to retrieve forecast data")

            # Format the forecast periods
            periods = forecast_data.get("properties", {}).get("periods", [])
            if not periods:
                return error_response("No forecast periods available")

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

            return message_response(forecast_text)
    else:
        return error_response("Invalid tool")



if __name__ == '__main__':
   app.run(port=os.getenv("PORT", 8080))