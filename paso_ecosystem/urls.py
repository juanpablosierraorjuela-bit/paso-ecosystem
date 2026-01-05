from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Incluimos las URLs de autenticación SaaS bajo /auth/ para mantener orden
    path('auth/', include('apps.core_saas.urls')),
    # Incluimos las URLs del negocio (marketplace, dashboard, etc.) en la raíz
    path('', include('apps.businesses.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
