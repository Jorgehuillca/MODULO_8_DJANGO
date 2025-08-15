import os
import re
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image
from .models import CompanyData

class CompanyService:
    """
    Servicio para manejar logos de empresa.
    """

    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    LOGO_FOLDER = 'company'

    @staticmethod
    def sanitize_file_name(filename):
        """
        Limpia el nombre del archivo (solo letras, números y guiones bajos).
        """
        filename = filename.lower()
        filename = re.sub(r'[^a-z0-9]+', '_', filename)
        filename = filename.strip('_')
        return filename or 'company'

    @staticmethod
    def generate_company_logo_file_name(company_name, original_filename):
        """
        Genera un nombre seguro para el logo.
        """
        ext = os.path.splitext(original_filename)[1].lower().lstrip('.')
        if ext not in CompanyService.ALLOWED_EXTENSIONS:
            raise ValueError(f"Formato no permitido. Solo {', '.join(CompanyService.ALLOWED_EXTENSIONS)}")
        clean_name = CompanyService.sanitize_file_name(company_name)
        return os.path.join(CompanyService.LOGO_FOLDER, f"{clean_name}_logo.{ext}")

    @staticmethod
    def clear_company_folder():
        """
        Elimina todos los logos de la carpeta company/.
        """
        folder_path = os.path.join(settings.MEDIA_ROOT, CompanyService.LOGO_FOLDER)
        if os.path.exists(folder_path):
            _, files = default_storage.listdir(CompanyService.LOGO_FOLDER)
            for f in files:
                default_storage.delete(os.path.join(CompanyService.LOGO_FOLDER, f))

    @staticmethod
    def clear_company_logo(company):
        """
        Elimina solo el logo de una empresa específica.
        """
        if company.company_logo:
            if default_storage.exists(company.company_logo.name):
                default_storage.delete(company.company_logo.name)

    @staticmethod
    def process_logo(company, file):
        """
        Valida y guarda el logo.
        """
        try:
            # Validación de tamaño
            if file.size > CompanyService.MAX_FILE_SIZE:
                raise ValueError(f"El logo excede el tamaño máximo permitido de {CompanyService.MAX_FILE_SIZE} bytes.")

            # Validación de extensión
            ext = file.name.split('.')[-1].lower()
            if ext not in CompanyService.ALLOWED_EXTENSIONS:
                raise ValueError(f"Formato no permitido. Solo se aceptan: {', '.join(CompanyService.ALLOWED_EXTENSIONS)}")

            # Validación de integridad de imagen
            try:
                file.seek(0)
                with Image.open(file) as img:
                    img.verify()
                file.seek(0)
            except Exception as img_error:
                raise ValueError("El archivo no es una imagen válida o está corrupta")

            # Limpiar logo anterior de esta empresa específica
            CompanyService.clear_company_logo(company)

            # Guardar nuevo logo
            file_path = CompanyService.generate_company_logo_file_name(company.company_name, file.name)
            saved_path = default_storage.save(file_path, file)

            company.company_logo = saved_path
            company.save()
            return company

        except Exception as e:
            raise ValueError(f"Error al procesar el logo: {str(e)}")
    
    #nuevas funciones
    
    @staticmethod
    def show(company_id):
        """
        Retorna los datos de la empresa.
        """
        try:
            return CompanyData.objects.get(pk=company_id)
        except CompanyData.DoesNotExist:
            return None

    @staticmethod
    def store(data, file=None):
        """
        Crea o actualiza datos de la empresa y procesa el logo si se envía.
        """
        company_id = data.get('id')
        try:
            if company_id:
                company = CompanyData.objects.get(pk=company_id)
            else:
                company = CompanyData()

            # Validar nombre de la empresa
            company_name = data.get('company_name', '').strip()
            if not company_name:
                raise ValueError("El nombre de la empresa es requerido")
        
            company.company_name = company_name
            
            # Si hay archivo, procesamos el logo ANTES de guardar
            if file:
                # Validación de tamaño
                if file.size > CompanyService.MAX_FILE_SIZE:
                    raise ValueError(f"El logo excede el tamaño máximo permitido de {CompanyService.MAX_FILE_SIZE} bytes.")

                # Validación de extensión
                ext = file.name.split('.')[-1].lower()
                if ext not in CompanyService.ALLOWED_EXTENSIONS:
                    raise ValueError(f"Formato no permitido. Solo se aceptan: {', '.join(CompanyService.ALLOWED_EXTENSIONS)}")

                # Validación de integridad de imagen
                try:
                    file.seek(0)
                    with Image.open(file) as img:
                        img.verify()
                    file.seek(0)
                except Exception:
                    raise ValueError("El archivo no es una imagen válida o está corrupta")

                # Limpiar logo anterior de esta empresa específica si existe
                if company.pk:  # Solo si la empresa ya existía
                    CompanyService.clear_company_logo(company)

                # Guardar archivo del logo
                file_path = CompanyService.generate_company_logo_file_name(company_name, file.name)
                saved_path = default_storage.save(file_path, file)
                company.company_logo = saved_path

            # Guardamos UNA sola vez con todos los datos
            company.save()
            return company

        except CompanyData.DoesNotExist:
            raise ValueError("Empresa no encontrada")
        except Exception as e:
            raise ValueError(f"Error interno al guardar los datos: {str(e)}")
