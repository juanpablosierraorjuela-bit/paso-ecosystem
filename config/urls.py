from django.contrib import admin
from django.urls import path, include
from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # --- RUTAS PÚBLICAS FIJAS ---
    path('', views.home, name='home'),
    path('registro/', views.register, name='register'),
    
    # --- RUTAS DEL DUEÑO (Debe ir antes del slug) ---
    path('mi-negocio/', views.dashboard, name='dashboard'),
    
    # --- RUTAS DE RESERVA (Debe ir antes del slug si alguna coincide) ---
    path('reserva-exitosa/', views.booking_success, name='booking_success'), # Esta chocaba también
    path('reservar/<int:service_id>/', views.booking_create, name='booking_create'),
    
    # --- RUTAS DEL EMPLEADO (Debe ir antes del slug) ---
    path('soy-pro/', views.employee_dashboard, name='employee_dashboard'), # Esta chocaba también
    path('unete/<uuid:token>/', views.employee_join, name='employee_join'),

    # --- API & WEBHOOKS ---
    path('api/availability/', views.api_get_availability, name='api_availability'),
    path('api/webhooks/bold/', views.bold_webhook, name='bold_webhook'),

    # --- RUTAS DINÁMICAS (AL FINAL) ---
    # Esta línea captura cualquier texto (como 'mi-negocio' o 'soy-pro') si no se ha encontrado arriba.
    # Por eso SIEMPRE debe ir al final.
    path('<slug:slug>/', views.salon_detail, name='salon_detail'),
]