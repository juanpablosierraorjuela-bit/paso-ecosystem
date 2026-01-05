from django.urls import path
from .views import (
    home, marketplace, salon_detail, landing_businesses,
    RegisterOwnerView, booking_wizard, client_dashboard,
    OwnerDashboardView, owner_settings_view, OwnerServicesView,
    ServiceCreateView, ServiceUpdateView, ServiceDeleteView,
    OwnerEmployeesView, EmployeeCreateView, employee_dashboard
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('marketplace/', marketplace, name='marketplace'),
    # AQUÍ ESTÁ LA CLAVE: Mapeamos la URL del HTML a la vista correcta
    path('registro-negocio/', RegisterOwnerView.as_view(), name='register_owner'),
    path('salon/<int:salon_id>/', salon_detail, name='salon_detail'),
    path('booking/<int:salon_id>/', booking_wizard, name='booking_wizard'),
    
    # Rutas de Dashboard
    path('dashboard/', OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/settings/', owner_settings_view, name='owner_settings'),
    path('dashboard/services/', OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/services/new/', ServiceCreateView.as_view(), name='service_create'),
    path('dashboard/services/<int:pk>/edit/', ServiceUpdateView.as_view(), name='service_update'),
    path('dashboard/services/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service_delete'),
    path('dashboard/employees/', OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/employees/new/', EmployeeCreateView.as_view(), name='employee_create'),
    
    path('client/dashboard/', client_dashboard, name='client_dashboard'),
    path('employee/dashboard/', employee_dashboard, name='employee_dashboard'),
]
