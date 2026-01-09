from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('mi-perfil/', views.client_dashboard, name='client_dashboard'),
    path('ingreso-exitoso/', views.dispatch_user, name='dispatch'),
    path('', views.home, name='home'),
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]