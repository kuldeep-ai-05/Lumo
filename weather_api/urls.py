from django.urls import path
from .views import WeatherAPIView, CurrentWeatherView

urlpatterns = [
    path('weather/', WeatherAPIView.as_view(), name='weather-api'),
    path('weather/now/', CurrentWeatherView.as_view(), name='current-weather'),
]
