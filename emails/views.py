from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import EmailRequestSerializer
from .services import EmailService

User = get_user_model()

class EmailController(APIView):
    def post(self, request):
        serializer = EmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        type_email = serializer.validated_data['type_email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        EmailService.send_verification_email(user, type_email)
        return Response({"message": "Código enviado correctamente"}, status=status.HTTP_200_OK)

def dashboard_email(request):
    return render(request, 'dashboard_email.html')

def email_restore(request):
    return render(request, 'emails/email_restore.html')

def password_restore(request):
    return render(request, 'emails/password_restore.html')

def verification(request):
    return render(request, 'emails/verification.html')