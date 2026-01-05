import os

# ==========================================
# 1. ACTUALIZAR BASE.HTML (Agregar Navbar)
# ==========================================
base_html_content = """{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PASO Ecosistema{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/landing.css' %}">
    <style>
        /* Navbar integrado */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.2rem 5%;
            background: rgba(0, 0, 0, 0.95);
            border-bottom: 1px solid #333;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .nav-brand { font-size: 1.5rem; font-weight: bold; color: white; text-decoration: none; }
        .nav-links { display: flex; gap: 20px; align-items: center; }
        .nav-item { color: #ccc; text-decoration: none; font-size: 0.95rem; transition: color 0.3s; }
        .nav-item:hover { color: #d4af37; }
        .btn-nav { padding: 8px 20px; border-radius: 50px; font-size: 0.9rem; text-decoration: none; }
        .btn-login { border: 1px solid #666; color: white; }
        .btn-action { background: #d4af37; color: black; font-weight: bold; }
    </style>
</head>
<body>
    
    <nav class="navbar">
        <a href="{% url 'home' %}" class="nav-brand">PASO.</a>
        <div class="nav-links">
            <a href="{% url 'marketplace:home' %}" class="nav-item">Marketplace</a>
            
            {% if user.is_authenticated %}
                <span class="nav-item">Hola, {{ user.first_name|default:user.username }}</span>
                {% if user.is_staff %}
                    <a href="/admin/" class="btn-nav btn-action">Admin</a>
                {% else %}
                    <a href="#" class="btn-nav btn-action">Mi Panel</a>
                {% endif %}
                <form action="{% url 'logout' %}" method="post" style="display:inline;">
                    {% csrf_token %}
                    <button type="submit" class="nav-item" style="background:none; border:none; cursor:pointer;">Salir</button>
                </form>
            {% else %}
                <a href="{% url 'login' %}" class="btn-nav btn-login">Entrar</a>
                <a href="{% url 'register_owner' %}" class="btn-nav btn-action">Registrar Negocio</a>
            {% endif %}
        </div>
    </nav>

    {% if messages %}
        <div style="background: #d4af37; color: black; padding: 10px; text-align: center; font-weight: bold;">
            {% for message in messages %}
                {{ message }}
            {% endfor %}
        </div>
    {% endif %}

    {% block content %}{% endblock %}

    <footer class="footer">
        <div class="brand">{{ PASO_SETTINGS.site_name|default:"PASO Ecosistema" }}</div>
        <div class="copyright">© 2026 - Belleza Inteligente</div>
        <div class="socials">
            {% if PASO_SETTINGS.instagram_link %}<a href="{{ PASO_SETTINGS.instagram_link }}" target="_blank" style="color:#ccc">Instagram</a>{% endif %}
        </div>
    </footer>
</body>
</html>
"""

# ==========================================
# 2. ARREGLAR HOME.HTML (Enlace roto)
# ==========================================
home_html_content = """{% extends 'base.html' %}

{% block content %}
<div class="hero">
    <h1>Belleza Inteligente.</h1>
    <p>El primer ecosistema digital que conecta la excelencia con la necesidad. Sin esperas. Sin errores.</p>
    
    <div class="action-buttons">
        <a href="{% url 'marketplace:home' %}" class="btn btn-primary">Buscar Servicios</a>
        <a href="{% url 'register_owner' %}" class="btn btn-outline">Registrar Negocio</a>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 3. CREAR MARKETPLACE (Vistas y URLs)
# ==========================================
# apps/marketplace/views.py
marketplace_views = """from django.shortcuts import render

def marketplace_home(request):
    return render(request, 'marketplace/index.html')
"""

# apps/marketplace/urls.py (NO EXISTÍA, LO CREAMOS)
marketplace_urls = """from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
]
"""

# templates/marketplace/index.html (NO EXISTÍA)
marketplace_template = """{% extends 'base.html' %}

{% block content %}
<div style="padding: 100px 5%; text-align: center; color: white;">
    <h1 style="color: #d4af37; font-size: 3rem;">Explora el Ecosistema</h1>
    <p style="margin-bottom: 40px; font-size: 1.2rem;">Encuentra los mejores salones y profesionales de tu ciudad.</p>
    
    <div style="border: 1px dashed #444; padding: 50px; border-radius: 10px;">
        <p>🚧 El Buscador Inteligente está en construcción 🚧</p>
        <br>
        <a href="{% url 'home' %}" class="btn-nav btn-login">Volver al Inicio</a>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 4. CONECTAR URLS PRINCIPALES (Config)
# ==========================================
config_urls = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('marketplace/', include('apps.marketplace.urls')), # NUEVA RUTA
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

# ==========================================
# 🛠️ FUNCIÓN DE ESCRITURA
# ==========================================
def write_file(path, content):
    print(f"📝 Actualizando: {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("🚀 INICIANDO CONEXIÓN DEL SISTEMA...")
    
    write_file('templates/base.html', base_html_content)
    write_file('templates/home.html', home_html_content)
    write_file('apps/marketplace/views.py', marketplace_views)
    write_file('apps/marketplace/urls.py', marketplace_urls)
    write_file('templates/marketplace/index.html', marketplace_template)
    write_file('config/urls.py', config_urls)
    
    print("\n✅ Archivos conectados.")
    print("👉 Ahora ejecuta estos comandos para subir los cambios:")
    print("   git add .")
    print('   git commit -m "Fix: Navbar Login y Marketplace"')
    print("   git push origin main")

if __name__ == "__main__":
    main()