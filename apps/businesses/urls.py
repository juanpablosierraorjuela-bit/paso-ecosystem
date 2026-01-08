from django.urls import path
from . import views

urlpatterns = [
    # --- DASHBOARD DUEÑO ---
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('configuracion/', views.owner_settings, name='owner_settings'),
    
    # --- GESTIÓN DE SERVICIOS ---
    # Aquí estaba el error: antes buscaba 'services_list', ahora apunta a 'owner_services'
    path('servicios/', views.owner_services, name='owner_services'), 
    path('servicios/crear/', views.service_create, name='service_create'),
    path('servicios/editar/<int:pk>/', views.service_update, name='service_update'),
    path('servicios/eliminar/<int:pk>/', views.service_delete, name='service_delete'),
    
    # --- GESTIÓN DE EMPLEADOS ---
    path('empleados/', views.owner_employees, name='owner_employees'),
    path('empleados/crear/', views.employee_create, name='employee_create'),
    path('empleados/editar/<int:pk>/', views.employee_update, name='employee_update'),
    path('empleados/eliminar/<int:pk>/', views.employee_delete, name='employee_delete'),
    
    # --- DASHBOARD EMPLEADO ---
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('mi-horario/', views.employee_schedule, name='employee_schedule'),
    
    # --- VERIFICACIÓN DE CITAS ---
    path('citas/verificar/<int:pk>/', views.verify_booking, name='verify_booking'),
]
