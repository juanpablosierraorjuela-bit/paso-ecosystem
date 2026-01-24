from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Nota: No usamos app_name='core' porque en settings.py las redirecciones 
# están configuradas a nombres globales como 'dispatch' y 'home'.

urlpatterns = [
    # Página principal / Marketplace
    path('', views.home, name='home'),
    
    # Landing page para dueños de negocio
    path('soluciones-negocio/', views.landing_owners, name='landing_owners'),
    
    # Autenticación y Registro
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Gestión de Sesión y Perfil
    # 'dispatch' es el destino tras el login exitoso según settings.py
    path('dispatch/', views.dispatch_user, name='dispatch'), 
    path('mi-perfil/', views.client_dashboard, name='client_dashboard'),
]