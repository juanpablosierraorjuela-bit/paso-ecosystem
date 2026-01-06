from django.urls import path
from . import views

urlpatterns = [
    # Rutas simples y directas
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('soluciones-negocios/', views.pain_landing, name='pain_landing'),
    
    # AQUÍ ESTABA EL ERROR: Quitamos .as_view() porque ahora es una función
    path('registro-negocio/', views.OwnerRegisterView, name='register_owner'),
]
