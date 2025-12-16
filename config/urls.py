from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Importamos las vistas desde apps.users.views
from apps.users.views import home, register, dashboard_view, create_salon_view, salon_detail

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),

    # --- Vistas Principales ---
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create-salon/', create_salon_view, name='create_salon'),
    
    # Perfil público del salón (Slug)
    path('salon/<slug:slug>/', salon_detail, name='salon_detail'),

    # --- Autenticación (Login/Logout estándar de Django) ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

# Configuración para servir imágenes en modo DEBUG (Local)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)