from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # CAMBIO DE SEGURIDAD: Admin oculto
    path('control-maestro-seguro/', admin.site.urls),
    
    path('', include('apps.core.urls')),
    path('negocio/', include('apps.businesses.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)