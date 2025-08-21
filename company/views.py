from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.conf import settings
from django.shortcuts import render #para la vista html
import os

from .models import CompanyData
from .serializers import CompanyDataSerializer, UploadImageRequest
from .services import CompanyService


class CompanyDataViewSet(viewsets.ModelViewSet):
    queryset = CompanyData.objects.all()
    serializer_class = CompanyDataSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_logo(self, request, pk=None):
        """Sube y procesa el logo de la empresa."""
        try:
            company = self.get_object()
        except Http404:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UploadImageRequest(data=request.data)
        if serializer.is_valid():
            try:
                CompanyService.process_logo(company, serializer.validated_data['logo'])
                return Response({"message": "Logo subido correctamente"}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def show_logo(self, request, pk=None):
        """Muestra el logo de la empresa."""
        try:
            company = self.get_object()
        except Http404:
            raise Http404("Empresa no encontrada")

        if not company.company_logo:
            raise Http404("La empresa no tiene logo")

        file_path = os.path.join(settings.MEDIA_ROOT, company.company_logo.name)
        if not os.path.exists(file_path):
            raise Http404("Archivo de logo no encontrado")

        return FileResponse(open(file_path, 'rb'))

    @action(detail=True, methods=['delete'])
    def delete_logo(self, request, pk=None):
        """Elimina el logo de la empresa."""
        company = self.get_object()
        CompanyService.clear_company_logo(company)  # Cambio aquí
        company.company_logo = None
        company.save()
        return Response({"message": "Logo eliminado correctamente"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def store(self, request):
        """Crea o actualiza datos de la empresa y procesa el logo si se envía."""
        # Extraer datos del formulario correctamente
        data = request.data  # <-- funciona para JSON y form-data
        
        # Intentar obtener el archivo con diferentes nombres
        file = request.FILES.get('logo') or request.FILES.get('company_logo')
    
        try:
            company = CompanyService.store(data, file)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        if not company:
            return Response({"error": "No se pudo crear/actualizar la empresa"}, 
                    status=status.HTTP_400_BAD_REQUEST)

        serializer = CompanyDataSerializer(company, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def show(self, request, pk=None):
        try:
            company = self.get_object()
            serializer = self.get_serializer(company)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Http404:
            return Response({
                'status': 'error',
                'message': 'Empresa no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """Sobrescribe el update para preservar el logo al actualizar el nombre"""
        instance = self.get_object()
        
        # Si hay archivo de logo en la request, usamos el store method
        if 'logo' in request.FILES or 'company_logo' in request.FILES:
            return super().update(request, *args, **kwargs)
        
        # Si solo actualizamos datos sin logo, preservamos el logo existente
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            # Guardamos el logo actual antes de la actualización
            current_logo = instance.company_logo
            serializer.save()
            # Restauramos el logo si no se envió uno nuevo
            if current_logo and not instance.company_logo:
                instance.company_logo = current_logo
                instance.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

def company_form_view(request):
    """Vista para el formulario de gestión de empresas"""
    return render(request, 'company/company_form.html')



