# emails/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    type_email = serializers.ChoiceField(choices=['verification', 'password_reset', 'change_email'])

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No existe un usuario con este correo.")
        return value
