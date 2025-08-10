from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import CompanyData
from .serializers import UploadImageRequest
from .services import CompanyService
from django.http import FileResponse, Http404
import os
from django.conf import settings
from .serializers import CompanyDataSerializer 

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_logo(request, company_id):
    """
    Sube y procesa el logo de la empresa.
    """
    try:
        company = CompanyData.objects.get(pk=company_id)
    except CompanyData.DoesNotExist:
        return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UploadImageRequest(data=request.data)
    if serializer.is_valid():
        try:
            CompanyService.process_logo(company, serializer.validated_data['logo'])
            return Response({"message": "Logo subido correctamente"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def show_logo(request, company_id):
    """
    Muestra el logo de la empresa.
    """
    try:
        company = CompanyData.objects.get(pk=company_id)
    except CompanyData.DoesNotExist:
        raise Http404("Empresa no encontrada")

    if not company.company_logo:
        raise Http404("Logo no disponible")

    file_path = os.path.join(settings.MEDIA_ROOT, company.company_logo.name)
    if not os.path.exists(file_path):
        raise Http404("Archivo de logo no encontrado")

    return FileResponse(open(file_path, 'rb'))


@api_view(['DELETE'])
def delete_logo(request, company_id):
    """
    Elimina el logo de la empresa.
    """
    try:
        company = CompanyData.objects.get(pk=company_id)
    except CompanyData.DoesNotExist:
        return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    CompanyService.clear_company_folder()
    company.company_logo = None
    company.save()

    return Response({"message": "Logo eliminado correctamente"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def show_company(request, company_id):
    """
    Obtiene los datos de una empresa.
    """
    company = CompanyService.show(company_id)
    if not company:
        return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompanyDataSerializer(company)
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def store_company(request):
    """
    Crea o actualiza datos de la empresa y procesa el logo si se envía.
    """
    file = request.FILES.get('logo')
    company = CompanyService.store(request.data, file)

    if not company:
        return Response({"error": "No se pudo crear/actualizar la empresa"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CompanyDataSerializer(company)
    return Response(serializer.data, status=status.HTTP_200_OK)

