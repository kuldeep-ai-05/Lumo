from django.urls import path
from .views import WeatherAPIView, CurrentWeatherView

urlpatterns = [
    path('', WeatherAPIView.as_view(), name='weather-api'), # Changed
    path('now/', CurrentWeatherView.as_view(), name='current-weather'), # Changed
]