from django.urls import path
from .views import (
    dashboard_email,
    email_restore,
    password_restore,
    verification,
    EmailController
)

urlpatterns = [
    path('dashboard/', dashboard_email, name='dashboard_email'),
    path('email_restore/', email_restore, name='email_restore'),
    path('password_restore/', password_restore, name='password_restore'),
    path('verification/', verification, name='verification'),
    path('send-email/', EmailController.as_view(), name='send_email'),
]
