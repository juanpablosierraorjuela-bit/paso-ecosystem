from django.urls import path
from . import views

urlpatterns = [
    # Paneles de Control
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('configuracion/', views.settings_view, name='settings_view'),

    # Gestión de Servicios
    path('servicios/', views.services_list, name='services_list'),
    path('servicios/editar/<int:pk>/', views.service_edit, name='service_edit'),
    path('servicios/eliminar/<int:pk>/', views.service_delete, name='service_delete'),

    # Gestión de Equipo (Empleados)
    path('equipo/', views.employees_list, name='employees_list'),
    path('equipo/eliminar/<int:pk>/', views.employee_delete, name='employee_delete'),
]