from django.urls import path
from . import views

urlpatterns = [
    # Vista Home (Función)
    path('', views.home, name='home'),
    
    # Vistas de Clase (Deben llevar .as_view())
    path('marketplace/', views.MarketplaceView.as_view(), name='marketplace'),
    path('negocios/', views.LandingBusinessesView.as_view(), name='landing_businesses'),
    path('registro-dueno/', views.RegisterOwnerView.as_view(), name='register_owner'),
    
    # Detalle
    path('salon/<int:pk>/', views.SalonDetailView.as_view(), name='salon_detail'),
    
    # Dashboard Dueño
    path('dashboard/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/servicios/', views.OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/servicios/nuevo/', views.ServiceCreateView.as_view(), name='service_create'),
    path('dashboard/servicios/<int:pk>/editar/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('dashboard/servicios/<int:pk>/eliminar/', views.ServiceDeleteView.as_view(), name='service_delete'),
    
    path('dashboard/empleados/', views.OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/empleados/nuevo/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('dashboard/empleados/<int:pk>/editar/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('dashboard/empleados/<int:pk>/eliminar/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    path('dashboard/configuracion/', views.OwnerSettingsView.as_view(), name='owner_settings'),
]
