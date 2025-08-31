from django.urls import path
from .views import ChatbotAPIView, ChatbotUIView

urlpatterns = [
    path('', ChatbotUIView.as_view(), name='chatbot-ui'),
    path('chat/', ChatbotAPIView.as_view(), name='chatbot-api'),
]
