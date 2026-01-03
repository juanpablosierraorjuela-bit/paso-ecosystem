from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.businesses import views as business_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth de la App core_saas
    path('auth/', include('apps.core_saas.urls')),
    
    # Incluimos las rutas de businesses (Donde ya arreglamos el marketplace)
    path('', include('apps.businesses.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
