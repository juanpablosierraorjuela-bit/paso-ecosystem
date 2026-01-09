from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # CAMBIO DE SEGURIDAD: Admin oculto
    path('control-maestro-seguro/', admin.site.urls),
    
    # Rutas de autenticación (Recuperar contraseña, etc.)
    path('cuentas/', include('django.contrib.auth.urls')),
    
    path('', include('apps.core.urls')),
    path('negocio/', include('apps.businesses.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)