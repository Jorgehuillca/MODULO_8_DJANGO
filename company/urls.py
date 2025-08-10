from django.urls import path
from .import views

urlpatterns = [
    path('<int:company_id>/show/', views.show_company, name='show_company'),
    path('store/', views.store_company, name='store_company'),
    path('<int:company_id>/logo/upload/', views.upload_logo, name='upload_logo'),
    path('<int:company_id>/logo/', views.show_logo, name='show_logo'),
    path('<int:company_id>/logo/delete/', views.delete_logo, name='delete_logo'),
]



