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
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Check if the user is asking about the weather
        if "weather" in prompt.lower():
            location = prompt.split(" ")[-1].strip("?")
            try:
                weather_response = requests.get(f'http://127.0.0.1:8000/api/weather/?location={location}')
                weather_response.raise_for_status()
                weather_data = weather_response.json()
                prompt = f"The user is asking about the weather in {location}. The current weather is: {weather_data['condition']} with a temperature of {weather_data['temperature_celsius']} degrees Celsius. Please answer the user's question based on this information: {prompt}"
            except requests.exceptions.RequestException as e:
                return Response({"error": f"Error connecting to weather service: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except Exception as e:
                prompt = f"The user is asking about the weather in {location}, but I could not retrieve the weather information. Please inform the user about this issue and ask them to try again. The original prompt was: {prompt}"

        # Check if the user wants to play music
        elif "play" in prompt.lower() and ("spotify" in prompt.lower() or "music" in prompt.lower()):
            sp = get_spotify_client(request.session)
            if not sp:
                return Response({"response": "You need to authorize with Spotify first. Please go to /api/spotify/login to authorize."})

            devices = sp.devices()
            if not devices['devices']:
                return Response({"response": "No active Spotify device found. Please open Spotify on one of your devices and try again."})

            if "playlist" in prompt.lower():
                # Play a playlist
                try:
                    playlist_name = prompt.split("play ")[-1].split(" playlist")[0]
                except:
                    playlist_name = "workout" # default playlist

                playlists = sp.current_user_playlists()
                playlist_uri = None
                for playlist in playlists['items']:
                    if playlist_name.lower() in playlist['name'].lower():
                        playlist_uri = playlist['uri']
                        break

                if not playlist_uri:
                    return Response({"response": f"Could not find a playlist named '{playlist_name}'."})

                sp.start_playback(device_id=devices['devices'][0]['id'], context_uri=playlist_uri)
                return Response({"response": f"Now playing your '{playlist_name}' playlist on Spotify."})
            else:
                # Play a song
                try:
                    song_name = prompt.split("play ")[-1]
                except:
                    return Response({"response": "Please specify a song to play."})

                results = sp.search(q=song_name, type="track", limit=1)
                if not results['tracks']['items']:
                    return Response({"response": f"Could not find a song named '{song_name}'."})

                song_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(device_id=devices['devices'][0]['id'], uris=[song_uri])
                return Response({"response": f"Now playing '{song_name}' on Spotify."})

        elif ("pause" in prompt.lower() or "unpause" in prompt.lower() or "resume" in prompt.lower()) and "spotify" in prompt.lower():
            sp = get_spotify_client(request.session)
            if not sp:
                return Response({"response": "You need to authorize with Spotify first. Please go to /api/spotify/login to authorize."})

            if "pause" in prompt.lower():
                sp.pause_playback()
                return Response({"response": "Playback paused."})
            else:
                sp.start_playback()
                return Response({"response": "Playback resumed."})

        # Send the prompt to the Gemini API
        try:
            response = model.generate_content(prompt)
            return Response({"response": response.text}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error communicating with Gemini API: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
