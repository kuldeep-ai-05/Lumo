from django.urls import path
from .views import SpotifyLogin, SpotifyCallback, NowPlayingView

urlpatterns = [
    path('spotify/login', SpotifyLogin.as_view(), name='spotify-login'),
    path('spotify/callback', SpotifyCallback.as_view(), name='spotify-callback'),
    path('spotify/now-playing/', NowPlayingView.as_view(), name='now-playing'),
]
