from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Importamos las vistas
from apps.users.views import home, register, dashboard_view, create_salon_view
from apps.businesses.views import salon_settings_view, employee_settings_view, salon_detail

urlpatterns = [
    path('admin/', admin.site.urls),

    # Vistas Generales
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create-salon/', create_salon_view, name='create_salon'),
    
    # Paneles Específicos
    path('dashboard/settings/', salon_settings_view, name='salon_settings'),
    path('dashboard/employee/', employee_settings_view, name='employee_settings'), # <--- NUEVA

    # Perfil y Reserva
    path('salon/<slug:slug>/', salon_detail, name='salon_detail'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)