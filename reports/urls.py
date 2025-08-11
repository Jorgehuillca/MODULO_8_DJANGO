from django.urls import path
from . import views

urlpatterns = [
    # Ruta para obtener la cantidad de citas por terapeuta en una fecha dada
    # URL: /appointments-per-therapist/
    # Vista asociada: get_number_appointments_per_therapist
    path(
        'appointments-per-therapist/',
        views.get_number_appointments_per_therapist,
        name='appointments_per_therapist'
    ),

    # Ruta para obtener el listado de pacientes agrupados por terapeuta en una fecha dada
    # URL: /patients-by-therapist/
    # Vista asociada: get_patients_by_therapist
    path(
        'patients-by-therapist/',
        views.get_patients_by_therapist,
        name='patients_by_therapist'
    ),
]
