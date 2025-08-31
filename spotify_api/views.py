import os
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

def get_spotify_client(session):
    token_info = session.get('spotify_token_info', None)
    if not token_info:
        return None

    auth_manager = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-modify-playback-state user-read-playback-state playlist-read-private",
    )

    if auth_manager.is_token_expired(token_info):
        token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
        session['spotify_token_info'] = token_info

    return Spotify(auth=token_info['access_token'])

class SpotifyLogin(APIView):
    def get(self, request, *args, **kwargs):
        auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope="user-modify-playback-state user-read-playback-state playlist-read-private",
        )
        return redirect(auth_manager.get_authorize_url())

class SpotifyCallback(APIView):
    def get(self, request, *args, **kwargs):
        auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope="user-modify-playback-state user-read-playback-state playlist-read-private",
        )
        code = request.GET.get("code")
        token_info = auth_manager.get_access_token(code)

        # Store the token info in the session
        # In a production app, you would want to store this more securely, e.g., in a database
        request.session['spotify_token_info'] = token_info

        return redirect('/')  # Redirect to a success page or the main UI

class NowPlayingView(APIView):
    def get(self, request, *args, **kwargs):
        sp = get_spotify_client(request.session)
        if not sp:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        track = sp.current_playback()
        if not track or not track['item'] or not track['is_playing']:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        track_info = {
            'name': track['item']['name'],
            'artist': track['item']['artists'][0]['name'],
            'album_art': track['item']['album']['images'][0]['url'],
            'is_playing': track['is_playing']
        }
        return Response(track_info)