from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Públicas
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('salon/<int:salon_id>/', views.salon_detail, name='salon_detail'),
    path('negocios/', views.landing_businesses, name='landing_businesses'),
    
    # Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register_owner/', views.RegisterOwnerView.as_view(), name='register_owner'),

    # Redirección inteligente (Dueño vs Empleado)
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Rutas Dueño
    path('dashboard/owner/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/services/', views.OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/employees/', views.OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/settings/', views.OwnerSettingsView.as_view(), name='owner_settings'),

    # Rutas Servicios
    path('dashboard/services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('dashboard/services/edit/<int:pk>/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('dashboard/services/delete/<int:pk>/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # Rutas Empleados (Dueño creando empleados)
    path('dashboard/employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),

    # Rutas Panel Empleado
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
]
