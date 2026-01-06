from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    path('services/', views.services_list, name='services'),
    path('employees/', views.employees_list, name='employees'),
    path('schedule/', views.schedule_config, name='schedule'),
    path('settings/', views.business_settings, name='settings'),
    
    # Redirección de compatibilidad
    path('panel/', views.owner_dashboard, name='panel_negocio'),
]
