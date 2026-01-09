from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    
    # NUEVA RUTA PARA LA LANDING
    path('soluciones-negocio/', views.landing_owners, name='landing_owners'),
    
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dispatch/', views.dispatch_user, name='dispatch'),
    path('mi-perfil/', views.client_dashboard, name='client_dashboard'),
]