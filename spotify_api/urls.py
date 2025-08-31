from django.urls import path
from .views import SpotifyLogin, SpotifyCallback, NowPlayingView

urlpatterns = [
    path('login', SpotifyLogin.as_view(), name='spotify-login'), # Changed
    path('callback', SpotifyCallback.as_view(), name='spotify-callback'), # Changed
    path('now-playing/', NowPlayingView.as_view(), name='now-playing'), # Changed
]