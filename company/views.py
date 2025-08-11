from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.conf import settings
import os

from .models import CompanyData
from .serializers import CompanyDataSerializer, UploadImageRequest
from .services import CompanyService


class CompanyDataViewSet(viewsets.ModelViewSet):
    queryset = CompanyData.objects.all()
    serializer_class = CompanyDataSerializer
    parser_classes = [MultiPartParser, FormParser]

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
        company = self.get_object()
        if not company.company_logo:
            raise Http404("Logo no disponible")

        file_path = os.path.join(settings.MEDIA_ROOT, company.company_logo.name)
        if not os.path.exists(file_path):
            raise Http404("Archivo de logo no encontrado")

        return FileResponse(open(file_path, 'rb'))

    @action(detail=True, methods=['delete'])
    def delete_logo(self, request, pk=None):
        """Elimina el logo de la empresa."""
        company = self.get_object()
        CompanyService.clear_company_folder()
        company.company_logo = None
        company.save()
        return Response({"message": "Logo eliminado correctamente"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def store(self, request):
        """Crea o actualiza datos de la empresa y procesa el logo si se envía."""
        file = request.FILES.get('logo')
        company = CompanyService.store(request.data, file)

        if not company:
            return Response({"error": "No se pudo crear/actualizar la empresa"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CompanyDataSerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def show(self, request, pk=None):
        """Obtiene los datos de una empresa."""
        try:
            company = self.get_object()
        except Http404:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyDataSerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)



