from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from decimal import Decimal

from .services import StatisticsService
from .serializers import StatisticsResource
from base_models.models import Appointment, Therapist, Patient, PaymentType


class StatisticsViewSetTestCase(APITestCase):
    """Tests para StatisticsViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('statistics-get-statistics')
        
    def test_get_statistics_without_parameters(self):
        """Test error cuando no se envían parámetros"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_get_statistics_invalid_date_format(self):
        """Test error con formato de fecha inválido"""
        response = self.client.get(self.url, {
            'start': '2024/01/01',  
            'end': '2024-01-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_get_statistics_start_date_greater_than_end_date(self):
        """Test error cuando start_date > end_date"""
        response = self.client.get(self.url, {
            'start': '2024-01-31',
            'end': '2024-01-01'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    @patch('app_statistics.views.StatisticsService')
    def test_get_statistics_success(self, mock_service_class):
        """Test respuesta exitosa"""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_statistics.return_value = {
            'terapeutas': [],
            'tipos_pago': {},
            'metricas': {'ttlpacientes': 10, 'ttlsesiones': 20, 'ttlganancias': 1000.0}
        }
        
        response = self.client.get(self.url, {
            'start': '2024-01-01',
            'end': '2024-01-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.get_statistics.assert_called_once()


class StatisticsServiceTestCase(TestCase):
    """Tests para StatisticsService"""
    
    def setUp(self):
        self.service = StatisticsService()
        self.start_date = date(2024, 1, 1)
        self.end_date = date(2024, 1, 31)
        
        # Crear datos de prueba básicos
        self.therapist = Therapist.objects.create(
            name='Juan',
            paternal_lastname='Pérez',
            maternal_lastname='González'
        )
        
        self.patient = Patient.objects.create(name='Paciente Test')
        
        self.payment_type = PaymentType.objects.create(name='Efectivo')
        
    def test_get_metricas_principales_without_appointments(self):
        """Test métricas principales sin citas"""
        result = self.service.get_metricas_principales(self.start_date, self.end_date)
        
        self.assertEqual(result['ttlpacientes'], 0)
        self.assertEqual(result['ttlsesiones'], 0)
        self.assertIsNone(result['ttlganancias'])
        
    def test_get_metricas_principales_with_appointments(self):
        """Test métricas principales con citas"""
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),
            patient=self.patient,
            therapist=self.therapist,
            payment=Decimal('100.00')
        )
        
        result = self.service.get_metricas_principales(self.start_date, self.end_date)
        
        self.assertEqual(result['ttlpacientes'], 1)
        self.assertEqual(result['ttlsesiones'], 1)
        self.assertEqual(result['ttlganancias'], Decimal('100.00'))
        
    def test_get_tipos_de_pago_empty(self):
        """Test tipos de pago sin datos"""
        result = self.service.get_tipos_de_pago(self.start_date, self.end_date)
        
        self.assertEqual(result, {})
        
    def test_get_tipos_de_pago_with_data(self):
        """Test tipos de pago con datos"""
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),
            patient=self.patient,
            therapist=self.therapist,
            payment_type=self.payment_type
        )
        
        result = self.service.get_tipos_de_pago(self.start_date, self.end_date)
        
        self.assertIn('Efectivo', result)
        self.assertEqual(result['Efectivo'], 1)
        
    def test_get_rendimiento_terapeutas_empty(self):
        """Test rendimiento terapeutas sin datos"""
        result = self.service.get_rendimiento_terapeutas(self.start_date, self.end_date)
        
        self.assertEqual(result, [])
        
    def test_get_rendimiento_terapeutas_with_data(self):
        """Test rendimiento terapeutas con datos"""
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),
            patient=self.patient,
            therapist=self.therapist,
            payment=Decimal('100.00')
        )
        
        result = self.service.get_rendimiento_terapeutas(self.start_date, self.end_date)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], self.therapist.id)
        self.assertEqual(result[0]['sesiones'], 1)
        self.assertEqual(result[0]['ingresos'], 100.0)
        self.assertIn('raiting', result[0])
        
    def test_get_ingresos_por_dia_semana_empty(self):
        """Test ingresos por día sin datos"""
        result = self.service.get_ingresos_por_dia_semana(self.start_date, self.end_date)
        
        self.assertEqual(result, {})
        
    def test_get_ingresos_por_dia_semana_with_data(self):
        """Test ingresos por día con datos"""
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),  # Lunes
            patient=self.patient,
            therapist=self.therapist,
            payment=Decimal('100.00')
        )
        
        result = self.service.get_ingresos_por_dia_semana(self.start_date, self.end_date)
        
        self.assertIn('Lunes', result)
        self.assertEqual(result['Lunes'], 100.0)
        
    def test_get_sesiones_por_dia_semana_with_data(self):
        """Test sesiones por día con datos"""
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),  # Lunes
            patient=self.patient,
            therapist=self.therapist
        )
        
        result = self.service.get_sesiones_por_dia_semana(self.start_date, self.end_date)
        
        self.assertIn('Lunes', result)
        self.assertEqual(result['Lunes'], 1)
        
    def test_get_tipos_pacientes_empty(self):
        """Test tipos de pacientes sin datos"""
        result = self.service.get_tipos_pacientes(self.start_date, self.end_date)
        
        self.assertEqual(result['c'], 0)
        self.assertEqual(result['cc'], 0)
        
    def test_get_tipos_pacientes_with_data(self):
        """Test tipos de pacientes con datos"""
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),
            patient=self.patient,
            therapist=self.therapist,
            appointment_type='C'
        )
        
        Appointment.objects.create(
            appointment_date=date(2024, 1, 16),
            patient=self.patient,
            therapist=self.therapist,
            appointment_type='CC'
        )
        
        result = self.service.get_tipos_pacientes(self.start_date, self.end_date)
        
        self.assertEqual(result['c'], 1)
        self.assertEqual(result['cc'], 1)
        
    def test_get_statistics_complete(self):
        """Test método principal get_statistics"""
        result = self.service.get_statistics(self.start_date, self.end_date)
        
        # Verificar que retorna todas las claves esperadas
        expected_keys = ['terapeutas', 'tipos_pago', 'metricas', 'ingresos', 'sesiones', 'tipos_pacientes']
        for key in expected_keys:
            self.assertIn(key, result)
            
    def test_excluded_deleted_appointments(self):
        """Test que excluye citas eliminadas"""
        # Crear cita eliminada
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),
            patient=self.patient,
            therapist=self.therapist,
            payment=Decimal('100.00'),
            deleted_at=datetime.now()
        )
        
        result = self.service.get_metricas_principales(self.start_date, self.end_date)
        
        # No debe contar la cita eliminada
        self.assertEqual(result['ttlpacientes'], 0)
        self.assertEqual(result['ttlsesiones'], 0)


class DashboardViewTestCase(TestCase):
    """Tests para dashboard view"""
    
    def test_dashboard_view_renders(self):
        """Test que dashboard renderiza correctamente"""
        url = reverse('statistics_dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')


class SerializersTestCase(TestCase):
    """Tests básicos para serializers"""
    
    def test_statistics_resource_serializer(self):
        """Test serializer principal"""
        data = {
            'metricas': {
                'ttlpacientes': 10,
                'ttlsesiones': 20,
                'ttlganancias': 1000.0
            }
        }
        
        serializer = StatisticsResource(data)
        result = serializer.data
        
        self.assertIn('metricas', result)
        

class IntegrationTestCase(TestCase):
    """Tests de integración"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear datos de prueba
        self.therapist = Therapist.objects.create(
            name='Ana',
            paternal_lastname='García',
            maternal_lastname='López'
        )
        self.patient = Patient.objects.create(name='Test Patient')
        
    def test_full_statistics_flow(self):
        """Test flujo completo"""
        # Crear appointment
        Appointment.objects.create(
            appointment_date=date(2024, 1, 15),
            patient=self.patient,
            therapist=self.therapist,
            payment=Decimal('150.00'),
            appointment_type='C'
        )
        
        url = reverse('statistics-get-statistics')
        response = self.client.get(url, {
            'start': '2024-01-01',
            'end': '2024-01-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        data = response.data
        self.assertIn('terapeutas', data)
        self.assertIn('metricas', data)
        self.assertIn('tipos_pacientes', data)
        
        # Verificar que hay datos
        self.assertEqual(data['metricas']['ttlpacientes'], 1)
        self.assertEqual(data['metricas']['ttlsesiones'], 1)
