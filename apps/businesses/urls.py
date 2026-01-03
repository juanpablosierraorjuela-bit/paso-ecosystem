from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Públicas
    path('', views.home, name='home'),
    path('negocios/', views.landing_businesses, name='landing_businesses'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('salon/<int:salon_id>/', views.salon_detail, name='salon_detail'),
    
    # Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register_owner/', views.RegisterOwnerView.as_view(), name='register_owner'),

    # Dashboard Dueño (Aquí arreglamos los botones caídos)
    path('dashboard/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/services/', views.OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/employees/', views.OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/settings/', views.OwnerSettingsView.as_view(), name='owner_settings'),
]
