from django.urls import path, include
from . import views

#app_name = 'reports'  # Opcional, pero recomendado si usas namespaced URLs

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    # Ruta para obtener la cantidad de citas por terapeuta en una fecha dada
    path('appointments-per-therapist/', views.get_number_appointments_per_therapist, name='appointments_per_therapist'),

    # Ruta para obtener el listado de pacientes agrupados por terapeuta en una fecha dada
    path('patients-by-therapist/', views.get_patients_by_therapist, name='patients_by_therapist'),

    # Ruta para obtener el resumen de caja diaria agrupado por tipo de pago
    path('daily-cash/', views.get_daily_cash, name='daily_cash'),

    # Ruta para obtener citas entre dos fechas dadas (inclusive)
    path('appointments-between-dates/', views.get_appointments_between_dates, name='appointments_between_dates'),
    # Nuevas URLs para exportar
    path('pdf/citas-terapeuta/', views.pdf_citas_terapeuta, name='pdf_citas_terapeuta'),
    path('pdf/pacientes-terapeuta/', views.pdf_pacientes_terapeuta, name='pdf_pacientes_terapeuta'),
    path('pdf/resumen-caja/', views.pdf_resumen_caja, name='pdf_resumen_caja'),
    path('excel/citas-rango/', views.exportar_excel_citas, name='exportar_excel_citas'),
    path('statistics/', include('app_statistics.urls')),
]
