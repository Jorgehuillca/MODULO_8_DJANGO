from rest_framework.routers import DefaultRouter
from app_statistics.views import StatisticsViewSet, dashboard_view
from django.urls import path, include

router = DefaultRouter()
router.register(r'', StatisticsViewSet, basename='statistics')

urlpatterns = [
    path('dashboard/', dashboard_view, name='statistics_dashboard'),
    path('',include(router.urls)),
]


