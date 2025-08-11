from django.test import TestCase, RequestFactory
from reports.services.report_service import ReportService
from reports.views import get_number_appointments_per_therapist, get_patients_by_therapist
from reports.models import Therapist, Appointment, Patient, PaymentType
from datetime import date

class ReportServiceTest(TestCase):
    def setUp(self):
        # Crear datos iniciales para las pruebas: terapeuta, paciente, tipo de pago y cita
        self.therapist = Therapist.objects.create(
            name="Juan",
            paternal_lastname="Perez",
            maternal_lastname="Lopez"
        )
        self.patient = Patient.objects.create(
            name="Ana",
            paternal_lastname="Gomez",
            maternal_lastname="Diaz",
            document_number="12345678",
            primary_phone="987654321"
        )
        self.payment_type = PaymentType.objects.create(name="EFECTIVO")

        self.appointment = Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=100,
            payment_type=self.payment_type,  # Se pasa la instancia, no el id
            appointment_hour="10:00"
        )

        # Instancia del servicio que se va a probar
        self.report_service = ReportService()

    def test_get_appointments_count_by_therapist(self):
        # Crear una petición GET simulada con fecha actual
        factory = RequestFactory()
        request = factory.get('/reports/appointments-per-therapist/', {'date': date.today().strftime("%Y-%m-%d")})

        # Ejecutar el método del servicio
        response = self.report_service.get_appointments_count_by_therapist(request)

        # Verificar que el resultado contiene las claves esperadas
        self.assertIn('therapists_appointments', response)
        self.assertIn('total_appointments_count', response)

        # Verificar que solo hay un terapeuta y que su conteo es correcto
        self.assertEqual(len(response['therapists_appointments']), 1)
        self.assertEqual(response['total_appointments_count'], 1)

        therapist_data = response['therapists_appointments'][0]
        self.assertEqual(therapist_data['id'], self.therapist.id)

    def test_get_patients_by_therapist(self):
        # Crear petición GET con fecha actual
        factory = RequestFactory()
        request = factory.get('/reports/patients-by-therapist/', {'date': date.today().strftime("%Y-%m-%d")})

        # Ejecutar el método que obtiene pacientes por terapeuta
        response = self.report_service.get_patients_by_therapist(request)

        # Validar que la respuesta es una lista y tiene al menos un terapeuta
        self.assertIsInstance(response, list)
        self.assertGreaterEqual(len(response), 1)

        # Validar estructura del primer terapeuta en la lista
        first = response[0]
        self.assertIn('therapist_id', first)
        self.assertIn('therapist', first)
        self.assertIn('patients', first)
        self.assertIsInstance(first['patients'], list)
        self.assertGreaterEqual(len(first['patients']), 1)

        patient = first['patients'][0]
        self.assertIn('patient_id', patient)
        self.assertIn('patient', patient)
        self.assertIn('appointments', patient)

class ReportViewsTest(TestCase):
    def setUp(self):
        # Preparar datos para pruebas de vistas: terapeuta, paciente, tipo de pago y cita
        self.factory = RequestFactory()
        self.therapist = Therapist.objects.create(
            name="Juan",
            paternal_lastname="Perez",
            maternal_lastname="Lopez"
        )
        self.patient = Patient.objects.create(
            name="Ana",
            paternal_lastname="Gomez",
            maternal_lastname="Diaz",
            document_number="12345678",
            primary_phone="987654321"
        )
        self.payment_type = PaymentType.objects.create(name="EFECTIVO")

        self.appointment = Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=100,
            payment_type=self.payment_type,
            appointment_hour="10:00"
        )

    def test_get_number_appointments_per_therapist_view(self):
        # Crear petición GET simulada
        request = self.factory.get('/reports/appointments-per-therapist/', {'date': date.today().strftime("%Y-%m-%d")})

        # Ejecutar la vista
        response = get_number_appointments_per_therapist(request)

        # Validar que la respuesta HTTP fue exitosa y contiene datos esperados
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'therapists_appointments', response.content)

    def test_get_patients_by_therapist_visew(self):
        # Crear petición GET simulada
        request = self.factory.get('/reports/patients-by-therapist/', {'date': date.today().strftime("%Y-%m-%d")})

        # Ejecutar la vista
        response = get_patients_by_therapist(request)

        # Validar que la respuesta HTTP fue exitosa y contiene datos esperados
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'therapist', response.content)

#ejecutar esto para el test: python manage.py test reports