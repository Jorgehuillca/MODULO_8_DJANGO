from rest_framework import serializers
from .models import CompanyData
import os

class UploadImageRequest(serializers.Serializer):
    logo = serializers.ImageField()

    def _get_file_size(self, value):
        # Intenta obtener size directamente
        size = getattr(value, 'size', None)
        if size:
            return size

        # Si no, intenta por el file-like object (sin consumirlo)
        file_obj = getattr(value, 'file', value)
        try:
            cur = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(cur)
            return size
        except Exception:
            # último recurso: leer y medir (resetea el puntero si puede)
            try:
                content = file_obj.read()
                size = len(content)
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                return size
            except Exception:
                return 0

    def validate_logo(self, value):
        max_size_mb = 2
        size = self._get_file_size(value)

        if size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"El logo no puede superar los {max_size_mb} MB.")

        # Validación de formato (igual que antes, con fallback)
        try:
            fmt = value.image.format.lower()
            if fmt not in ['jpeg', 'jpg', 'png']:
                raise serializers.ValidationError("Solo se permiten imágenes JPG o PNG.")
        except AttributeError:
            filename_ext = value.name.split('.')[-1].lower()
            if filename_ext not in ['jpg', 'jpeg', 'png']:
                raise serializers.ValidationError("Solo se permiten imágenes JPG o PNG.")

        return value

class CompanyDataSerializer(serializers.ModelSerializer):
    """
    Serializer principal para datos de empresa
    Expone los métodos que YA tienes en tu modelo
    """
    logo_url = serializers.SerializerMethodField()
    has_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyData
        fields = ['id', 'company_name', 'company_logo', 'logo_url', 'has_logo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'logo_url', 'has_logo']
    
    def get_logo_url(self, obj):
        # Llama al método que YA está en tu modelo
        return obj.get_logo_url()
    
    def get_has_logo(self, obj):
        # Llama al método que YA está en tu modelo
        return obj.has_logo()