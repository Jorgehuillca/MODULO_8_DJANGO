
from django.db import models

class CompanyData(models.Model):
    company_name = models.CharField(max_length=255)
    company_logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def get_logo_url(self):
        if self.company_logo:
            return self.company_logo.url
        return '/static/img/default-logo.png'  # o el path a un logo por defecto

    def has_logo(self):
        return bool(self.company_logo)

    def __str__(self):
        return self.company_name
