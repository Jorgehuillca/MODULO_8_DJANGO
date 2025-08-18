from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyDataViewSet, company_form_view 

router = DefaultRouter()
router.register(r'company', CompanyDataViewSet, basename='company')

urlpatterns = [
    path('', include(router.urls)),
    path('form/', company_form_view, name='company_form'),
]




