from rest_framework import serializers
from .models import CompanyData

class UploadImageRequest(serializers.Serializer):
    logo = serializers.ImageField()
    def validate_logo(self, value):
        max_size_mb = 2
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"El logo no puede superar los {max_size_mb} MB.")
        
        # Agregar solo un try/except para seguridad:
        try:
            if value.image.format.lower() not in ['jpeg', 'jpg', 'png']:
                raise serializers.ValidationError("Solo se permiten imágenes JPG o PNG.")
        except AttributeError:
            # Para SVG u otros formatos sin 'image' attribute
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