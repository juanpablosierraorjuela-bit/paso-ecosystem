from django.contrib import admin
from django.urls import path, include
# 1. IMPORTAR ESTO ES OBLIGATORIO:
from django.contrib.auth import views as auth_views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 2. ESTAS SON LAS RUTAS QUE FALTABAN (Login y Logout):
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Conectamos las URLs de la app businesses a la raíz del sitio
    path('', include('apps.businesses.urls')),
]

# Soporte para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)