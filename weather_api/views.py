import os
from dotenv import load_dotenv
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Load environment variables from .env file
load_dotenv()

class CurrentWeatherView(APIView):
    def get(self, request, *args, **kwargs):
        lat = request.query_params.get('lat', None)
        lon = request.query_params.get('lon', None)
        location = request.query_params.get('location', "London") # Default to London if no coords

        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return Response(
                {"error": "Server configuration error: Weather API key is not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "appid": api_key,
            "units": "metric"
        }

        if lat and lon:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location

        try:
            api_response = requests.get(base_url, params=params)
            api_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Error connecting to weather service: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        data = api_response.json()

        if data.get("cod") != 200:
            error_message = data.get("message", "Unknown error")
            return Response(
                {"error": f"Could not find weather for '{location}': {error_message}"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            processed_data = {
                "location": f"{data['name']}, {data['sys']['country']}",
                "temperature_celsius": data['main']['temp'],
                "condition": data['weather'][0]['description'],
                "icon": data['weather'][0]['icon']
            }
        except (KeyError, IndexError) as e:
            return Response(
                {"error": f"Failed to parse weather data: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(processed_data, status=status.HTTP_200_OK)

class WeatherAPIView(APIView):
    """
    An API View to get weather data for a specific location.
    """

    def get(self, request, *args, **kwargs):
        # Get location from query parameters
        location = request.query_params.get('location', None)
        if not location:
            return Response({"error": "Location parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get API key from environment variables
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return Response(
                {"error": "Server configuration error: Weather API key is not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Call the external weather API
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"
        }

        try:
            api_response = requests.get(base_url, params=params)
            api_response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Error connecting to weather service: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        data = api_response.json()

        if data.get("cod") != 200:
            error_message = data.get("message", "Unknown error")
            return Response(
                {"error": f"Could not find weather for '{location}': {error_message}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Process the data and return a simplified response
        try:
            processed_data = {
                "location": f"{data['name']}, {data['sys']['country']}",
                "temperature_celsius": data['main']['temp'],
                "condition": data['weather'][0]['description'],
                "humidity_percent": data['main']['humidity']
            }
        except (KeyError, IndexError) as e:
            return Response(
                {"error": f"Failed to parse weather data: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(processed_data, status=status.HTTP_200_OK)