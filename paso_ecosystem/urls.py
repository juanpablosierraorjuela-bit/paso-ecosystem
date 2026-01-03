from django.contrib import admin
from django.urls import path
from apps.businesses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('negocio/<slug:slug>/', views.salon_detail, name='salon_detail'),

    # Booking
    path('reserva/iniciar/', views.booking_wizard_start, name='booking_wizard_start'),
    path('reserva/profesional/', views.booking_step_employee, name='booking_step_employee'),
    path('reserva/fecha/', views.booking_step_datetime, name='booking_step_datetime'),
    path('reserva/contacto/', views.booking_step_contact, name='booking_step_contact'),
    path('reserva/crear/', views.booking_create, name='booking_create'),

    # Dashboards
    path('mi-panel/', views.client_dashboard, name='client_dashboard'),
    path('confirmar-pago/<int:booking_id>/', views.booking_confirm_payment, name='booking_confirm_payment'),

    # GESTIÓN DUEÑO (NUEVAS RUTAS)
    path('panel-negocio/', views.owner_dashboard, name='owner_dashboard'),
    path('panel-negocio/servicios/', views.owner_services, name='owner_services'),
    path('panel-negocio/empleados/', views.owner_employees, name='owner_employees'),
    path('panel-negocio/configuracion/', views.owner_settings, name='owner_settings'),

    # Auth
    path('login/', views.saas_login, name='saas_login'),
    path('logout/', views.saas_logout, name='saas_logout'),
    path('registro-negocio/', views.register_owner, name='register_owner'),
]