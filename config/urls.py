from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Importamos las vistas (incluyendo la nueva employee_join_view)
from apps.users.views import home, register, dashboard_view, create_salon_view, employee_join_view
from apps.businesses.views import salon_settings_view, employee_settings_view, salon_detail

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Vistas Generales ---
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # --- Rutas de Negocio (Dueños) ---
    path('create-salon/', create_salon_view, name='create_salon'),
    path('dashboard/settings/', salon_settings_view, name='salon_settings'),

    # --- Rutas de Empleado (Colaboradores) ---
    path('dashboard/employee/', employee_settings_view, name='employee_settings'),
    path('join-team/', employee_join_view, name='employee_join'), # <--- NUEVA RUTA

    # --- Perfil Público ---
    path('salon/<slug:slug>/', salon_detail, name='salon_detail'),

    # --- Autenticación ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)