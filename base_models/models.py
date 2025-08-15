from django.db import models


# Tablas mínimas para las llaves foráneas
class AppointmentStatus(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

class Patient(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    paternal_lastname = models.CharField(max_length=100, null=True, blank=True)  # Apellido paterno
    maternal_lastname = models.CharField(max_length=100, null=True, blank=True)  # Apellido materno
    document_number = models.CharField(max_length=20, null=True, blank=True)  # Número de documento (DNI, etc.)
    primary_phone = models.CharField(max_length=20, null=True, blank=True)  # Teléfono principal de contacto

    def __str__(self):
        return f"{self.paternal_lastname} {self.maternal_lastname} {self.name}".strip()


class Region(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

class Province(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

class District(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

class DocumentType(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)

class Country(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)


# Tabla PaymentType
class PaymentType(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

# Tabla Therapist
class Therapist(models.Model):
    code = models.CharField(max_length=50, null=True, blank=True)
    document_number = models.CharField(max_length=50, null=True, blank=True)
    paternal_lastname = models.CharField(max_length=50, null=True, blank=True)
    maternal_lastname = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    personal_reference = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, null=True, blank=True)
    primary_phone = models.CharField(max_length=80, null=True, blank=True)
    secondary_phone = models.CharField(max_length=80, null=True, blank=True)
    email = models.CharField(max_length=60, null=True, blank=True)
    address = models.CharField(max_length=60, null=True, blank=True)

    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.paternal_lastname} {self.maternal_lastname} {self.name}".strip()

# Tabla Appointment

class Appointment(models.Model):
    appointment_date = models.DateField(null=True, blank=True)
    appointment_hour = models.TimeField(null=True, blank=True)
    ailments = models.CharField(max_length=255, null=True, blank=True)
    diagnosis = models.CharField(max_length=255, null=True, blank=True)
    surgeries = models.CharField(max_length=255, null=True, blank=True)
    reflexology_diagnostics = models.CharField(max_length=255, null=True, blank=True)
    medications = models.CharField(max_length=255, null=True, blank=True)
    observation = models.CharField(max_length=255, null=True, blank=True)
    initial_date = models.DateField(null=True, blank=True)
    final_date = models.DateField(null=True, blank=True)
    appointment_type = models.CharField(max_length=255, null=True, blank=True)
    room = models.IntegerField(null=True, blank=True)
    social_benefit = models.BooleanField(null=True, blank=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ticket_number = models.IntegerField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    appointment_status = models.ForeignKey(AppointmentStatus, on_delete=models.SET_NULL, null=True, blank=True)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    therapist = models.ForeignKey(Therapist, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        patient_name = self.patient.name if self.patient else "No patient"
        return f"Appointment #{self.id} - {patient_name} - {self.appointment_date}"

