from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 1. INICIO (Raíz): Lleva a la Landing Page
    path('', views.home, name='home'),

    # 2. MARKETPLACE: Donde aparecen los negocios
    path('marketplace/', views.marketplace, name='marketplace'),

    # 3. ENTRAR: Login de usuarios (Redirige al login de admin o cliente)
    # Se asume que el template está en registration/login.html o users/login.html
    # Ajusta 'template_name' si tu archivo se llama diferente.
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 4. SOY NEGOCIO: Registro
    path('soy-negocio/', views.register_owner, name='registro_owner'),

    # 5. PANELES DE CONTROL
    path('dashboard/', views.dashboard, name='dashboard'), # Cliente
    path('admin-dashboard/', views.owner_dashboard, name='admin_dashboard'), # Dueño
    path('employee-panel/', views.employee_dashboard, name='employee_panel'), # Empleado

    # 6. API Y UTILIDADES
    path('api/available-slots/', views.get_available_slots_api, name='get_available_slots_api'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('api/telegram-test/', views.test_telegram_integration, name='test_telegram_integration'),
    
    # 7. RESERVAS Y PAGOS (Slugs y Webhooks)
    path('api/webhooks/bold/<int:salon_id>/', views.bold_webhook, name='bold_webhook'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    
    # Esta ruta siempre va AL FINAL porque captura cualquier texto como slug del salón
    path('<slug:salon_slug>/', views.booking_create, name='booking_create'),
]
