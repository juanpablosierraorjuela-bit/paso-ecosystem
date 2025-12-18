from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- VISTAS PRINCIPALES ---
    path('', views.home, name='home'),
    path('salon/<slug:slug>/', views.salon_detail, name='salon_detail'),
    
    # --- SISTEMA DE USUARIOS (Corregido) ---
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # --- DASHBOARD & NEGOCIOS ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/empleado/', views.employee_dashboard, name='employee_dashboard'),
    
    # --- CITAS & EMPLEADOS ---
    path('unete/<uuid:token>/', views.employee_join, name='employee_join'),
    path('reservar/<int:service_id>/', views.booking_create, name='booking_create'),
    path('reservar/exito/', views.booking_success, name='booking_success'),
    
    # --- WEBHOOKS & API ---
    path('api/availability/', views.api_get_availability, name='api_availability'),
    path('api/webhooks/bold/', views.bold_webhook, name='bold_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)