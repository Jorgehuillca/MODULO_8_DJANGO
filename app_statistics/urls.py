from rest_framework.routers import DefaultRouter
from app_statistics.views import StatisticsViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'statistics', StatisticsViewSet, basename='statistics')

urlpatterns = [
    path('',include(router.urls)),
]
