from django.http import JsonResponse, HttpResponse
from .services.report_service import ReportService
from django.shortcuts import render
from django_xhtml2pdf.utils import pdf_decorator
import xlsxwriter
import io
from datetime import datetime

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

def reports_dashboard(request):
    return render(request, 'reports.html')


@pdf_decorator(pdfname='citas_terapeuta.pdf')
def pdf_citas_terapeuta(request):
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    data = report_service.get_appointments_count_by_therapist(request)
    
    # Calcular porcentajes si no vienen en los datos
    if 'therapists_appointments' in data:
        total = data.get('total_appointments_count', 1)  # Evitar división por cero
        for therapist in data['therapists_appointments']:
            therapist['percentage'] = (therapist['appointments_count'] / total) * 100 if total > 0 else 0
    
    context = {
        'date': date,
        'data': data,
        'title': 'Citas por Terapeuta'
    }
    return render(request, 'pdf_templates/citas_terapeuta.html', context)

@pdf_decorator(pdfname='pacientes_por_terapeuta.pdf')
def pdf_pacientes_terapeuta(request):
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    data = report_service.get_patients_by_therapist(request)
    context = {
        'date': date,
        'data': data,
        'title': 'Pacientes por Terapeuta'
    }
    return render(request, 'pdf_templates/pacientes_terapeuta.html', context)

@pdf_decorator(pdfname='resumen_caja.pdf')
def pdf_resumen_caja(request):
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    data = report_service.get_daily_cash(request)
    
    # Calcular el total aquí en la vista
    total = sum(item['total_payment'] for item in data) if data else 0
    
    context = {
        'date': date,
        'data': data,
        'total': total,  # Pasamos el total calculado
        'title': 'Resumen de Caja Diaria'
    }
    return render(request, 'pdf_templates/resumen_caja.html', context)

def exportar_excel_citas(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    data = report_service.get_appointments_between_dates(request)
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Citas')
    
    # Formato para encabezados
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2c3e50',
        'font_color': 'white',
        'border': 1
    })
    
    # Escribir encabezados
    headers = ['Fecha', 'Hora', 'Terapeuta', 'Paciente', 'Pago', 'Tipo de Pago']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Escribir datos
    for row, appointment in enumerate(data, start=1):
        worksheet.write(row, 0, appointment.get('appointment_date', ''))
        worksheet.write(row, 1, appointment.get('appointment_hour', ''))
        worksheet.write(row, 2, appointment.get('therapist', ''))
        worksheet.write(row, 3, appointment.get('patient', ''))
        worksheet.write(row, 4, float(appointment.get('payment', 0)))
        worksheet.write(row, 5, appointment.get('payment_type', ''))
    
    # Ajustar anchos de columna
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('C:D', 30)
    worksheet.set_column('E:E', 12)
    worksheet.set_column('F:F', 15)
    
    workbook.close()
    output.seek(0)
    
    filename = f'citas_{start_date}_a_{end_date}.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
