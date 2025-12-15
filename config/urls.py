from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importamos las vistas
from apps.users.views import register
from apps.businesses.views import dashboard_view, create_salon_view, home, salon_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- PÁGINA DE INICIO ---
    path('', home, name='home'),
    
    # --- PERFIL PÚBLICO DEL SALÓN ---
    path('salon/<slug:slug>/', salon_detail, name='salon_detail'),

    # --- AUTENTICACIÓN ---
    path('accounts/login/', include('django.contrib.auth.urls')), 
    path('register/', register, name='register'),

    # --- PANEL DE CONTROL ---
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/create-salon/', create_salon_view, name='create_salon'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)