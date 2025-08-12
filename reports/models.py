'''
from django.db import models

class Therapist(models.Model):
    # Modelo para guardar los datos de un terapeuta
    name = models.CharField(max_length=100)  # Nombre del terapeuta
    paternal_lastname = models.CharField(max_length=100)  # Apellido paterno
    maternal_lastname = models.CharField(max_length=100)  # Apellido materno

    def __str__(self):
        return f"{self.paternal_lastname} {self.maternal_lastname} {self.name}".strip()

class Patient(models.Model):
    # Modelo para guardar los datos de un paciente
    name = models.CharField(max_length=100)  # Nombre del paciente
    paternal_lastname = models.CharField(max_length=100)  # Apellido paterno
    maternal_lastname = models.CharField(max_length=100)  # Apellido materno
    document_number = models.CharField(max_length=20)  # Número de documento (DNI, etc.)
    primary_phone = models.CharField(max_length=20)  # Teléfono principal de contacto

    def __str__(self):
        return f"{self.paternal_lastname} {self.maternal_lastname} {self.name}".strip()

class PaymentType(models.Model):
    # Modelo para tipos de pago, ej. efectivo, tarjeta, transferencia, etc.
    name = models.CharField(max_length=50)  # Nombre del tipo de pago

    def __str__(self):
        return self.name

class Appointment(models.Model):
    # Modelo para citas médicas o terapéuticas
    therapist = models.ForeignKey(Therapist,on_delete=models.SET_NULL,null=True,blank=True,related_name='appointments')  # Relación con terapeuta, puede ser nula (sin terapeuta asignado)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)  # Relación con paciente, obligatorio
    appointment_date = models.DateField()  # Fecha de la cita
    appointment_hour = models.TimeField()  # Hora de la cita
    payment = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)  # Monto pagado, puede ser nulo
    payment_type = models.ForeignKey(PaymentType,on_delete=models.SET_NULL,null=True,blank=True)  # Tipo de pago usado, puede ser nulo
    deleted_at = models.DateTimeField(null=True,blank=True)  # Fecha y hora de eliminación lógica (soft delete), si aplica

    def __str__(self):
        return f"Cita {self.appointment_date} {self.appointment_hour} - {self.patient}"
'''