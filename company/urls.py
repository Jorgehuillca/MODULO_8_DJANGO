from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyDataViewSet, company_view #xd

router = DefaultRouter()
router.register(r'company', CompanyDataViewSet, basename='company')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', company_view, name='company_details'),
    path('company/view/', company_view, name='company_view'),
]




