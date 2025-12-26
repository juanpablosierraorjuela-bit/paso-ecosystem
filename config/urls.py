from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import views as auth_views
from apps.businesses.views import (
    home as marketplace_view, booking_create, booking_success, dashboard,
    register_owner, owner_dashboard, employee_dashboard,
    delete_service, get_available_slots_api, test_telegram_integration,
    logout_view  # Importamos tu vista personalizada de logout
)

urlpatterns = [
    path('reserva-confirmada/<int:booking_id>/', booking_success, name='booking_success'),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="home_landing.html"), name='home'),
    path('negocios/', TemplateView.as_view(template_name="business_landing.html"), name='owner_landing'),
    path('unete-como-negocio/', RedirectView.as_view(url='/negocios/', permanent=True)),
    
    path('registro-negocio/', register_owner, name='registro_owner'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    
    # LOGOUT CORREGIDO: Usamos tu vista personalizada que permite GET
    path('logout/', logout_view, name='logout'),

    path('marketplace/', marketplace_view, name='marketplace'),
    path('reservar/<slug:salon_slug>/', booking_create, name='booking_create'),
    
    path('mis-citas/', dashboard, name='dashboard'),
    path('panel-admin/', owner_dashboard, name='admin_dashboard'),
    path('panel-empleado/', employee_dashboard, name='employee_panel'),
    path('borrar-servicio/<int:service_id>/', delete_service, name='delete_service'),

    # RUTA API PARA JAVASCRIPT
    path('api/get-slots/', get_available_slots_api, name='get_slots_api'),

    path('api/test-telegram/', test_telegram_integration, name='test_telegram'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
