# emails/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import EmailRequestSerializer
from .services import EmailService
from django.shortcuts import render
from types import SimpleNamespace

def email_panel(request):
    from types import SimpleNamespace
    user = SimpleNamespace(get_full_name=lambda: 'Usuario Demo', username='demo_user')
    code = 'ABC123'
    site_name = 'MiSistema'
    template = request.GET.get('template', 'unificar.html')
    email_type = request.GET.get('type', 'verify')

    context = {
        'user': user,
        'code': code,
        'email_type': email_type,
        'site_name': site_name,
        'template': template
    }
    return render(request, 'emails/panel.html', context)


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
