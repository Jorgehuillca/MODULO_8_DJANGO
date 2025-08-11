from django.http import JsonResponse
from .services.report_service import ReportService

report_service = ReportService()

def get_number_appointments_per_therapist(request):
    """
    Devuelve JSON con el número de citas por terapeuta para una fecha dada.
    """
    data = report_service.get_appointments_count_by_therapist(request)
    if isinstance(data, dict) and "error" in data:
        return JsonResponse(data, status=400)
    return JsonResponse(data, safe=False)

def get_patients_by_therapist(request):
    """
    Devuelve JSON con los pacientes agrupados por terapeuta para una fecha dada.
    """
    data = report_service.get_patients_by_therapist(request)
    if isinstance(data, dict) and "error" in data:
        return JsonResponse(data, status=400)
    return JsonResponse(data, safe=False)

def get_daily_cash(request):
    """
    Devuelve JSON con el resumen diario de efectivo agrupado por tipo de pago.
    """
    data = report_service.get_daily_cash(request)
    if isinstance(data, dict) and "error" in data:
        return JsonResponse(data, status=400)
    return JsonResponse(data, safe=False)

def get_appointments_between_dates(request):
    """
    Devuelve JSON con todas las citas entre dos fechas con info de paciente y terapeuta.
    """
    data = report_service.get_appointments_between_dates(request)
    if isinstance(data, dict) and "error" in data:
        return JsonResponse(data, status=400)
    return JsonResponse(data, safe=False)
