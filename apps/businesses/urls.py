from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('negocios/', views.landing_businesses, name='landing_businesses'),
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('salon/<int:pk>/', views.salon_detail, name='salon_detail'),
    path('reservar/inicio/', views.booking_wizard_start, name='booking_wizard_start'),
    path('reservar/empleado/', views.booking_step_employee, name='booking_step_employee'),
    path('reservar/calendario/', views.booking_step_calendar, name='booking_step_calendar'),
    path('reservar/confirmar/', views.booking_step_confirm, name='booking_step_confirm'),
    path('reservar/crear/', views.booking_create, name='booking_create'),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('dashboard/verificar/<int:pk>/', views.verify_booking, name='verify_booking'),
    path('dashboard/servicios/', views.owner_services, name='owner_services'),
    path('dashboard/servicios/nuevo/', views.service_create, name='service_create'),
    path('dashboard/servicios/<int:pk>/editar/', views.service_update, name='service_update'),
    path('dashboard/servicios/<int:pk>/eliminar/', views.service_delete, name='service_delete'),
    path('dashboard/empleados/', views.owner_employees, name='owner_employees'),
    path('dashboard/empleados/nuevo/', views.employee_create, name='employee_create'),
    path('dashboard/empleados/<int:pk>/editar/', views.employee_update, name='employee_update'),
    path('dashboard/empleados/<int:pk>/eliminar/', views.employee_delete, name='employee_delete'),
    path('dashboard/configuracion/', views.owner_settings, name='owner_settings'),
    path('empleado/', views.employee_dashboard, name='employee_dashboard'),
    path('empleado/horario/', views.employee_schedule, name='employee_schedule'),
]
