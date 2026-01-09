import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR URLS.PY (AGREGAR RUTAS DE AUTH)
# ==========================================
urls_path = BASE_DIR / 'config' / 'urls.py'

# Contenido corregido para urls.py
# Se asegura de incluir django.contrib.auth.urls bajo el prefijo 'cuentas/'
urls_content = """
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
"""

# ==========================================
# 2. ACTUALIZAR LOGIN.HTML (AGREGAR ENLACE)
# ==========================================
login_path = BASE_DIR / 'templates' / 'registration' / 'login.html'

html_login = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-20 px-4 relative overflow-hidden bg-black">
    <div class="absolute inset-0 opacity-40">
        <img src="https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?q=80&w=2070&auto=format&fit=crop" class="w-full h-full object-cover">
    </div>
    
    <div class="glass-panel max-w-md w-full p-10 rounded-3xl shadow-2xl relative z-10 border border-white/10">
        <div class="text-center mb-10">
            <h2 class="text-3xl font-serif font-bold text-gray-900">Bienvenido</h2>
            <p class="mt-2 text-sm text-gray-500">Accede a tu panel de control</p>
        </div>

        <form class="space-y-6" method="post" action="{% url 'login' %}">
            {% csrf_token %}
            {% if form.errors %}
                <div class="bg-red-50 text-red-600 p-3 rounded text-sm text-center mb-4">Credenciales inválidas.</div>
            {% endif %}

            <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Usuario</label>
                <input type="text" name="username" required class="block w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:outline-none transition">
            </div>

            <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Contraseña</label>
                <div class="relative">
                    <input type="password" name="password" id="loginPass" required class="block w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:outline-none transition pr-12">
                    <button type="button" onclick="togglePassword('loginPass', this)" class="absolute inset-y-0 right-0 px-4 text-gray-400 hover:text-black focus:outline-none flex items-center">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                    </button>
                </div>
                <div class="text-right mt-2">
                    <a href="{% url 'password_reset' %}" class="text-xs text-gray-500 hover:text-black underline transition">¿Olvidaste tu contraseña?</a>
                </div>
            </div>

            <button type="submit" class="w-full py-4 bg-black text-white font-bold rounded-xl hover:bg-gold transition duration-300 shadow-lg mt-4">
                INGRESAR
            </button>

            <div class="text-center mt-6 text-sm">
                <a href="{% url 'register_owner' %}" class="text-gray-500 hover:text-black transition">¿Nuevo aquí? <span class="font-bold underline">Crear cuenta</span></a>
            </div>
        </form>
    </div>
</div>

<script>
    function togglePassword(inputId, btn) {
        const input = document.getElementById(inputId);
        const icon = btn.querySelector('svg');
        if (input.type === "password") {
            input.type = "text";
            btn.classList.add('text-black');
            btn.classList.remove('text-gray-400');
        } else {
            input.type = "password";
            btn.classList.remove('text-black');
            btn.classList.add('text-gray-400');
        }
    }
</script>
{% endblock %}
"""

def execute_fix():
    print("🔑 IMPLEMENTANDO SISTEMA DE RECUPERACIÓN DE CONTRASEÑA...")

    # 1. Update URLs
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content.strip())
    print("✅ config/urls.py: Rutas de autenticación agregadas ('/cuentas/').")

    # 2. Update Login Template
    with open(login_path, 'w', encoding='utf-8') as f:
        f.write(html_login.strip())
    print("✅ templates/registration/login.html: Enlace '¿Olvidaste tu contraseña?' insertado.")

if __name__ == "__main__":
    execute_fix()