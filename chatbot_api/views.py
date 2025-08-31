import os
from dotenv import load_dotenv
import requests
import google.generativeai as genai
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables from .env file
load_dotenv()

class ChatbotUIView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'chatbot_api/index.html')

from spotify_api.views import get_spotify_client

class ChatbotAPIView(APIView):
    """
    An API View to interact with the Gemini chatbot.
    """

    def post(self, request, *args, **kwargs):
        # Get prompt from request body
        prompt = request.data.get('prompt', None)
        if not prompt:
            return Response({"error": "Prompt parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get Gemini API key from environment variables
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key or gemini_api_key == "YOUR_GEMINI_API_KEY_HERE":
            return Response(
                {"error": "Server configuration error: Gemini API key is not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Configure the Gemini API
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')

        # Check if the user is asking about the weather
        if "weather" in prompt.lower():
            import re
            match = re.search(r'weather(?: over| in)?\s+([a-zA-Z\s]+)(?: now)?', prompt.lower())
            location = "London" # Default location
            if match:
                location = match.group(1).strip()

            try:
                weather_response = requests.get(f'http://127.0.0.1:8000/api/weather/?location={location}')
                weather_response.raise_for_status()
                weather_data = weather_response.json()
                response_text = f"The weather in {weather_data['location']} is {weather_data['condition']} with a temperature of {weather_data['temperature_celsius']}°C."
                return Response({"response": response_text}, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                return Response({"response": f"I'm sorry, I couldn't get the weather information right now. Error: {e}"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"response": f"I'm sorry, I couldn't process the weather information. Error: {e}"}, status=status.HTTP_200_OK)

        # Check if the user wants to play music
        elif "play" in prompt.lower() and ("spotify" in prompt.lower() or "music" in prompt.lower()):
            sp = get_spotify_client(request.session)
            if not sp:
                return Response({"response": "You need to authorize with Spotify first. Please go to /api/spotify/login to authorize."})

            devices = sp.devices()
            if not devices['devices']:
                return Response({"response": "No active Spotify device found. Please open Spotify on one of your devices and try again."})

            active_device_id = devices['devices'][0]['id']

            if "playlist" in prompt.lower():
                # Play a playlist
                playlist_name = prompt.lower().split("play ")[-1].replace(" playlist", "").replace(" on spotify", "").strip()
                if not playlist_name:
                    return Response({"response": "Please specify a playlist to play."})

                playlists = sp.current_user_playlists()
                playlist_uri = None
                for playlist in playlists['items']:
                    if playlist_name in playlist['name'].lower():
                        playlist_uri = playlist['uri']
                        break

                if not playlist_uri:
                    return Response({"response": f"Could not find a playlist named '{playlist_name}'."})

                sp.start_playback(device_id=active_device_id, context_uri=playlist_uri)
                return Response({"response": f"Now playing your '{playlist_name}' playlist on Spotify."})
            else:
                # Play a song
                song_name = prompt.lower().split("play ")[-1].replace(" on spotify", "").strip()
                if not song_name:
                    return Response({"response": "Please specify a song to play."})

                results = sp.search(q=song_name, type="track", limit=1)
                if not results['tracks']['items']:
                    return Response({"response": f"Could not find a song named '{song_name}'."})

                song_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(device_id=active_device_id, uris=[song_uri])
                return Response({"response": f"Now playing '{song_name}' on Spotify."})

        elif "pause" in prompt.lower() and "spotify" in prompt.lower():
            sp = get_spotify_client(request.session)
            if not sp:
                return Response({"response": "You need to authorize with Spotify first. Please go to /api/spotify/login to authorize."})

            sp.pause_playback()
            return Response({"response": "Playback paused."})

        elif "resume" in prompt.lower() and "spotify" in prompt.lower():
            sp = get_spotify_client(request.session)
            if not sp:
                return Response({"response": "You need to authorize with Spotify first. Please go to /api/spotify/login to authorize."})

            sp.start_playback()
            return Response({"response": "Playback resumed."})

        # Send the prompt to the Gemini API
        try:
            response = model.generate_content(prompt)
            response_text = response.text if response.text else "I'm sorry, I don't have a response for that."
            return Response({"response": response_text}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"response": f"I'm sorry, I encountered an error communicating with Gemini: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
