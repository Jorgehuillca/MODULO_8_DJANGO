# emails/services.py
import random
from django.utils import timezone
from django.core.mail import send_mail
from django.db import transaction
from django.conf import settings
from .models import UserVerificationCode


class EmailService:

    @staticmethod
    @transaction.atomic
    def send_verification_email(user, type_email):
        """
        Envía un correo de verificación al usuario con un código único
        y maneja la expiración de códigos anteriores.
        """
        # Expira códigos anteriores
        UserVerificationCode.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).update(is_active=False)

        # Genera un código de 6 dígitos
        code = str(random.randint(100000, 999999))

        # Guarda en la base de datos
        verification = UserVerificationCode.objects.create(
            user=user,
            code=code,
            type_email=type_email,
            is_active=True,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )

        # Asunto y mensaje según tipo de email
        if type_email == 'verification':
            subject = 'Verificación de cuenta'
            message = f'Tu código de verificación es: {code}'
        elif type_email == 'password_reset':
            subject = 'Recuperación de contraseña'
            message = f'Usa este código para restablecer tu contraseña: {code}'
        elif type_email == 'change_email':
            subject = 'Cambio de correo electrónico'
            message = f'Código para confirmar el cambio: {code}'
        else:
            raise ValueError("Tipo de email no válido")

        # Envío del correo
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        return verification
