from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    # 1. Dashboard Principal (Tu vista se llama owner_dashboard)
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    
    # 2. Servicios
    path('services/', views.services_list, name='services'),
    
    # 3. Horarios (CORREGIDO: schedule_config en lugar de schedule_list)
    path('schedule/', views.schedule_config, name='schedule'),
    
    # 4. Empleados (Faltaba en tu archivo anterior)
    path('employees/', views.employees_list, name='employees'),
    
    # 5. Configuración (Faltaba en tu archivo anterior)
    path('settings/', views.business_settings, name='settings'),
    
    # Ruta 'panel' redirigida al dashboard para compatibilidad
    path('panel/', views.owner_dashboard, name='panel_negocio'),
]
