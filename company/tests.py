from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
import tempfile

from .models import CompanyData
from .services import CompanyService

# Configuración temporal para tests
TEST_MEDIA_ROOT = tempfile.mkdtemp()


class CompanyServiceTest(TestCase):
    
    def setUp(self):
        self.company = CompanyData.objects.create(company_name='Test Company')
    
    def test_sanitize_file_name(self):
        """Test limpiar nombre de archivo - CRÍTICO"""
        test_cases = [
            ("Mi Empresa 123!", "mi_empresa_123"),
            ("Empresa@#$%", "empresa"),
            ("", "company"),
        ]
        
        for input_name, expected in test_cases:
            result = CompanyService.sanitize_file_name(input_name)
            self.assertEqual(result, expected)
    
    def test_generate_company_logo_file_name_invalid_extension(self):
        """Test extensión no permitida - CRÍTICO"""
        with self.assertRaises(ValueError):
            CompanyService.generate_company_logo_file_name("Mi Empresa", "logo.gif")
    
    def test_show_existing_company(self):
        """Test obtener empresa existente"""
        company = CompanyService.show(self.company.id)
        self.assertEqual(company.id, self.company.id)
    
    def test_show_non_existing_company(self):
        """Test empresa inexistente"""
        company = CompanyService.show(99999)
        self.assertIsNone(company)
    
    def test_store_new_company(self):
        """Test crear nueva empresa - CRÍTICO"""
        data = {'company_name': 'Nueva Empresa'}
        company = CompanyService.store(data)
        
        self.assertIsNotNone(company)
        self.assertEqual(company.company_name, 'Nueva Empresa')
    
    def test_store_empty_company_name(self):
        """Test validación nombre vacío - CRÍTICO"""
        data = {'company_name': '   '}
        
        with self.assertRaises(ValueError) as context:
            CompanyService.store(data)
        
        self.assertIn("El nombre de la empresa es requerido", str(context.exception))
    
    def test_process_logo_too_large(self):
        """Test logo muy grande - CRÍTICO"""
        large_file = SimpleUploadedFile(
            "large.jpg", 
            b"x" * (3 * 1024 * 1024),  # 3MB
            content_type="image/jpeg"
        )
        
        with self.assertRaises(ValueError) as context:
            CompanyService.process_logo(self.company, large_file)
        
        self.assertIn("excede el tamaño máximo", str(context.exception))
    
    def test_process_logo_invalid_extension(self):
        """Test extensión inválida - CRÍTICO"""
        invalid_file = SimpleUploadedFile(
            "test.gif", 
            b"fake gif content", 
            content_type="image/gif"
        )
        
        with self.assertRaises(ValueError):
            CompanyService.process_logo(self.company, invalid_file)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CompanyDataViewSetTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.company = CompanyData.objects.create(company_name='Test Company')
        self.list_url = reverse('company-list')
    
    def get_detail_url(self, company_id, action=None):
        if action:
            return reverse(f'company-{action}', kwargs={'pk': company_id})
        return reverse('company-detail', kwargs={'pk': company_id})
    
    def test_list_companies(self):
        """Test listar empresas - BÁSICO"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_company(self):
        """Test crear empresa - CRÍTICO"""
        data = {'company_name': 'Nueva Empresa'}
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company_name'], 'Nueva Empresa')
    
    def test_get_company_detail(self):
        """Test obtener empresa específica"""
        url = self.get_detail_url(self.company.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Test Company')
    
    def test_update_company(self):
        """Test actualizar empresa"""
        url = self.get_detail_url(self.company.id)
        data = {'company_name': 'Empresa Actualizada'}
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Empresa Actualizada')
    
    def test_upload_logo_no_file(self):
        """Test subir logo sin archivo - CRÍTICO"""
        url = self.get_detail_url(self.company.id, 'upload-logo')
        response = self.client.post(url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_upload_logo_company_not_found(self):
        """Test upload logo empresa inexistente - CRÍTICO"""
        url = self.get_detail_url(99999, 'upload-logo')
        # Crear archivo simple para test
        fake_file = SimpleUploadedFile("test.jpg", b"fake", content_type="image/jpeg")
        data = {'logo': fake_file}
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_logo_success(self):
        """Test eliminar logo"""
        url = self.get_detail_url(self.company.id, 'delete-logo')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('eliminado', response.data['message'])
    
    def test_store_endpoint_real(self):
        """Test endpoint store SIN MOCK - CRÍTICO"""
        url = reverse('company-store')
        data = {'company_name': 'Store Real Test'}
        
        response = self.client.post(url, data, format='multipart')
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la empresa se creó
        created_company = CompanyData.objects.filter(company_name='Store Real Test').first()
        self.assertIsNotNone(created_company)
    
    def test_store_endpoint_failure(self):
        """Test store con nombre vacío"""
        url = reverse('company-store')
        data = {'company_name': '   '}  # Nombre vacío
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_show_action_success(self):
        """Test action show"""
        url = self.get_detail_url(self.company.id, 'show')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['company_name'], 'Test Company')
    
    def test_show_action_not_found(self):
        """Test action show empresa no encontrada"""
        url = self.get_detail_url(99999, 'show')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CompanyModelTest(TestCase):
    
    def test_company_creation(self):
        """Test crear empresa básica"""
        company = CompanyData.objects.create(company_name='Model Test')
        self.assertEqual(str(company), 'Model Test')
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)
    
    def test_company_logo_methods(self):
        """Test métodos de logo"""
        company = CompanyData.objects.create(company_name='Logo Test')
        
        # Sin logo
        self.assertFalse(company.has_logo())
        
        # URL por defecto
        logo_url = company.get_logo_url()
        self.assertIn('default-logo', logo_url)
    
    def test_company_uniqueness(self):
        """Test unicidad de nombres"""
        CompanyData.objects.create(company_name='Unique Test')
        
        with self.assertRaises(Exception):
            CompanyData.objects.create(company_name='Unique Test')


class IntegrationTest(TestCase):
    
    def test_complete_company_workflow(self):
        """Test flujo completo empresa - MUY CRÍTICO"""
        # 1. Crear empresa
        data = {'company_name': 'Workflow Test'}
        company = CompanyService.store(data)
        self.assertIsNotNone(company)
        
        # 2. Verificar que se creó
        retrieved = CompanyService.show(company.id)
        self.assertEqual(retrieved.company_name, 'Workflow Test')
        
        # 3. Actualizar empresa
        update_data = {
            'id': company.id,
            'company_name': 'Workflow Updated'
        }
        updated = CompanyService.store(update_data)
        self.assertEqual(updated.company_name, 'Workflow Updated')
    
    def test_api_to_service_integration(self):
        """Test integración API -> Service"""
        client = APIClient()
        
        # Crear via API
        data = {'company_name': 'Integration Test'}
        response = client.post(reverse('company-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        company_id = response.data['id']
        
        # Verificar via Service
        company = CompanyService.show(company_id)
        self.assertEqual(company.company_name, 'Integration Test')