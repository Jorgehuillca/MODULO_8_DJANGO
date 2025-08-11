from django.contrib import admin
from .models import Appointment, Therapist, PaymentType, Patient

admin.site.register(Therapist)
admin.site.register(Appointment)
admin.site.register(PaymentType)
admin.site.register(Patient)

