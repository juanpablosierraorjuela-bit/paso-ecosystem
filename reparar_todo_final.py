import os

def arreglar_archivo(ruta, reemplazos, nombre_archivo):
    if not os.path.exists(ruta):
        print(f"❌ No se encontró: {ruta}")
        return

    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    nuevo_contenido = contenido
    cambios = False
    
    for original, nuevo in reemplazos.items():
        if original in nuevo_contenido:
            nuevo_contenido = nuevo_contenido.replace(original, nuevo)
            cambios = True
    
    if cambios:
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        print(f"✅ ¡ARREGLADO! {nombre_archivo} ha sido corregido.")
    else:
        print(f"ℹ️ {nombre_archivo} ya estaba correcto o no se encontró el texto exacto.")

# --- 1. ARREGLAR apps/businesses/urls.py (El error actual) ---
path_business = os.path.join('apps', 'businesses', 'urls.py')
reemplazos_business = {
    "name='register_owner'": "name='registro_owner'",  # <--- ESTO CORRIGE EL ERROR ACTUAL
}
arreglar_archivo(path_business, reemplazos_business, "apps/businesses/urls.py")

# --- 2. ARREGLAR config/urls.py (Asegurar que el login no falle nunca más) ---
path_config = os.path.join('config', 'urls.py')
contenido_config_seguro = """from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de autenticación (Login y Logout)
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Conectamos las URLs de la app businesses a la raíz del sitio
    path('', include('apps.businesses.urls')),
]

# Soporte para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

# Reescribimos config/urls.py por completo para evitar conflictos raros
with open(path_config, 'w', encoding='utf-8') as f:
    f.write(contenido_config_seguro)
print(f"✅ ¡ARREGLADO! config/urls.py reescrito con la versión segura.")

print("\n🚀 LISTO JUAN PABLO. AHORA EJECUTA LOS COMANDOS DE GIT.")