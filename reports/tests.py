from django.test import TestCase, RequestFactory
from reports.services.report_service import ReportService
from reports.views import get_number_appointments_per_therapist, get_patients_by_therapist, get_daily_cash, get_appointments_between_dates
from base_models.models import Therapist, Appointment, Patient, PaymentType
from datetime import date

class ReportServiceTest(TestCase):
    """
    Pruebas unitarias para los métodos del servicio ReportService.
    """

    def setUp(self):
        """
        Crear datos iniciales comunes para todas las pruebas del servicio:
        terapeuta, paciente, tipo de pago y una cita.
        """
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

        self.report_service = ReportService()

    def test_get_appointments_count_by_therapist(self):
        """
        Verifica que el conteo de citas por terapeuta se obtiene correctamente.
        """
        factory = RequestFactory()
        request = factory.get(
            '/reports/appointments-per-therapist/',
            {'date': date.today().strftime("%Y-%m-%d")}
        )
        response = self.report_service.get_appointments_count_by_therapist(request)

        # Validaciones básicas de estructura y contenido
        self.assertIn('therapists_appointments', response)
        self.assertIn('total_appointments_count', response)
        self.assertEqual(len(response['therapists_appointments']), 1)
        self.assertEqual(response['total_appointments_count'], 1)

        therapist_data = response['therapists_appointments'][0]
        self.assertEqual(therapist_data['id'], self.therapist.id)

    def test_get_patients_by_therapist(self):
        """
        Verifica que se obtienen los pacientes agrupados por terapeuta.
        """
        factory = RequestFactory()
        request = factory.get(
            '/reports/patients-by-therapist/',
            {'date': date.today().strftime("%Y-%m-%d")}
        )
        response = self.report_service.get_patients_by_therapist(request)

        self.assertIsInstance(response, list)
        self.assertGreaterEqual(len(response), 1)

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

    def test_get_daily_cash(self):
        """
        Valida la suma diaria de efectivo agrupado por tipo de pago,
        y verifica el orden específico esperado.
        """
        factory = RequestFactory()
        # Crear varios tipos de pago
        coupon = PaymentType.objects.create(name="Cupón")
        efectivo = self.payment_type  # ya existe
        yape = PaymentType.objects.create(name="Yape")
        otro = PaymentType.objects.create(name="Transferencia")

        # Crear citas con diferentes pagos para la fecha de hoy
        Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=50,
            payment_type=coupon,
            appointment_hour="09:00"
        )
        Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=30,
            payment_type=efectivo,
            appointment_hour="11:00"
        )
        Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=20,
            payment_type=yape,
            appointment_hour="12:00"
        )
        Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=10,
            payment_type=otro,
            appointment_hour="13:00"
        )

        request = factory.get('/reports/daily-cash/', {'date': date.today().strftime("%Y-%m-%d")})
        response = self.report_service.get_daily_cash(request)

        self.assertIsInstance(response, list)

        # Validar orden de los tipos de pago según requisito
        tipos = [item['payment_type'] for item in response]
        self.assertEqual(tipos, ["Cupón", "EFECTIVO", "Yape", "Transferencia"])

        # Validar suma correcta para el tipo "Cupón"
        cupón = next(filter(lambda x: x['payment_type'] == "Cupón", response))
        self.assertEqual(cupón['total_payment'], 50.0)

    def test_get_appointments_between_dates(self):
        """
        Valida que se obtienen las citas en el rango de fechas indicado,
        con la información necesaria.
        """
        factory = RequestFactory()

        # Crear dos citas para la fecha actual
        Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=40,
            payment_type=self.payment_type,
            appointment_hour="14:00"
        )
        Appointment.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=date.today(),
            deleted_at=None,
            payment=60,
            payment_type=self.payment_type,
            appointment_hour="15:00"
        )

        start = date.today().strftime("%Y-%m-%d")
        end = date.today().strftime("%Y-%m-%d")
        request = factory.get('/reports/appointments-between-dates/', {'start_date': start, 'end_date': end})
        response = self.report_service.get_appointments_between_dates(request)

        self.assertIsInstance(response, list)
        self.assertGreaterEqual(len(response), 2)

        # Validar estructura de un elemento en la respuesta
        appointment = response[0]
        self.assertIn('appointment_id', appointment)
        self.assertIn('appointment_date', appointment)
        self.assertIn('appointment_hour', appointment)
        self.assertIn('therapist', appointment)
        self.assertIn('patient', appointment)
        self.assertIn('payment', appointment)
        self.assertIn('payment_type', appointment)


class ReportViewsTest(TestCase):
    """
    Pruebas para las vistas del módulo reports.
    """

    def setUp(self):
        """
        Crear datos comunes para las pruebas de vistas:
        terapeuta, paciente, tipo de pago y cita.
        """
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
        """
        Valida la respuesta de la vista que lista el número de citas por terapeuta.
        """
        request = self.factory.get('/reports/appointments-per-therapist/', {'date': date.today().strftime("%Y-%m-%d")})
        response = get_number_appointments_per_therapist(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'therapists_appointments', response.content)

    def test_get_patients_by_therapist_view(self):
        """
        Valida la respuesta de la vista que lista pacientes por terapeuta.
        """
        request = self.factory.get('/reports/patients-by-therapist/', {'date': date.today().strftime("%Y-%m-%d")})
        response = get_patients_by_therapist(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'therapist', response.content)

    def test_get_daily_cash_view(self):
        """
        Valida la respuesta de la vista que muestra el resumen de caja diaria.
        """
        request = self.factory.get('/reports/daily-cash/', {'date': date.today().strftime("%Y-%m-%d")})
        response = get_daily_cash(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'payment_type', response.content)

    def test_get_appointments_between_dates_view(self):
        """
        Valida la respuesta de la vista que lista citas entre dos fechas.
        """
        request = self.factory.get('/reports/appointments-between-dates/', {
            'start_date': date.today().strftime("%Y-%m-%d"),
            'end_date': date.today().strftime("%Y-%m-%d")
        })
        response = get_appointments_between_dates(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'appointment_id', response.content)
