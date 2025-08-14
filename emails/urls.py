# emails/urls.py
from django.urls import path
from .views import EmailController
from .views import email_panel

urlpatterns = [
     path('panel/', email_panel, name='email-panel'),
    path('send-code/', EmailController.as_view(), name='send-code'),
]
