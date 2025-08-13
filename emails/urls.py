# emails/urls.py
from django.urls import path
from .views import EmailController

urlpatterns = [
    path('send-code/', EmailController.as_view(), name='send-code'),
]
