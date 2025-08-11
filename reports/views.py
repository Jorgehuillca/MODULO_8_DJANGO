from django.http import JsonResponse
from .services.report_service import ReportService

# Crear una instancia del servicio que maneja la lógica de los reportes
report_service = ReportService()

def get_number_appointments_per_therapist(request):
    """
    Vista que recibe una petición HTTP y devuelve un JSON con el número de citas
    por terapeuta para una fecha dada (parámetro GET "date").
    """
    # Llamar al servicio para obtener los datos
    data = report_service.get_appointments_count_by_therapist(request)
    # Devolver los datos como JsonResponse
    return JsonResponse(data, safe=False)


def get_patients_by_therapist(request):
    """
    Vista que recibe una petición HTTP y devuelve un JSON con los pacientes
    agrupados por terapeuta para una fecha dada (parámetro GET "date").
    """
    # Llamar al servicio para obtener los datos
    data = report_service.get_patients_by_therapist(request)
    # Devolver los datos como JsonResponse
    return JsonResponse(data, safe=False)
