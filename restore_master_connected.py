import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
CORE_APP_DIR = os.path.join(BASE_DIR, "apps", "core_saas")

MASTER_HTML_PATH = os.path.join(TEMPLATES_DIR, "master.html")
MODELS_PATH = os.path.join(CORE_APP_DIR, "models.py")
CONTEXT_PATH = os.path.join(CORE_APP_DIR, "context_processors.py")
ADMIN_PATH = os.path.join(CORE_APP_DIR, "admin.py")

# --- 1. MODELO DE CONFIGURACIÓN (Para guardar tus redes en Admin) ---
CONTENIDO_MODELS = """from django.db import models

class PlatformSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Paso Ecosystem")
    whatsapp_number = models.CharField(max_length=20, help_text="Ej: 573001234567", blank=True, null=True)
    instagram_link = models.CharField(max_length=200, help_text="URL completa de Instagram", blank=True, null=True)
    footer_text = models.CharField(max_length=200, default="Todos los derechos reservados", blank=True)

    def __str__(self):
        return "Configuración General de la Plataforma"

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"
"""

# --- 2. ADMIN (Para que puedas editarlo) ---
CONTENIDO_ADMIN = """from django.contrib import admin
from .models import PlatformSettings

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'whatsapp_number', 'instagram_link')
    
    # Esto impide crear más de una configuración (Singleton)
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
"""

# --- 3. CONTEXT PROCESSOR (El puente entre la BD y el HTML) ---
CONTENIDO_CONTEXT = """from .models import PlatformSettings

def global_settings(request):
    # Busca la configuración, si no existe devuelve vacío para no romper nada
    settings = PlatformSettings.objects.first()
    return {'global_settings': settings}
"""

# --- 4. MASTER.HTML (DISEÑO BLANCO Y CONECTADO) ---
CONTENIDO_MASTER = """{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PASO | Gestión Inteligente</title>
    
    <link rel="icon" type="image/x-icon" href="{% static 'favicon.ico' %}">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;900&display=swap" rel="stylesheet">
    
    <style>
        /* ESTILO GLOBAL LIMPIO */
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: #ffffff; 
            color: #111;
            display: flex; 
            flex-direction: column; 
            min-height: 100vh; 
        }

        /* NAVBAR BLANCA Y MINIMALISTA */
        .navbar { 
            background-color: #ffffff; 
            padding: 18px 0; 
            border-bottom: 1px solid #f2f2f2; /* Línea sutil */
        }
        .navbar-brand { 
            font-weight: 900; 
            font-size: 1.6rem; 
            letter-spacing: -1px; 
            color: #000 !important; 
        }
        .nav-link { 
            font-weight: 500; 
            color: #555 !important; 
            margin-left: 20px; 
            font-size: 0.95rem;
            transition: color 0.2s;
        }
        .nav-link:hover { color: #000 !important; }

        /* BOTONES ELEGANTES */
        .btn-dark-paso {
            background-color: #000;
            color: #fff;
            padding: 8px 25px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s;
            border: 1px solid #000;
        }
        .btn-dark-paso:hover {
            background-color: #333;
            color: #fff;
            transform: translateY(-1px);
        }
        .btn-outline-paso {
            background-color: transparent;
            color: #000;
            padding: 8px 25px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.9rem;
            border: 1px solid #ddd;
            transition: all 0.3s;
        }
        .btn-outline-paso:hover {
            border-color: #000;
        }

        /* CONTENIDO PRINCIPAL */
        main { flex: 1; }

        /* FOOTER BLANCO (ESTILO BACKUP) */
        footer { 
            background-color: #ffffff; /* FONDO BLANCO */
            color: #333; 
            padding: 60px 0; 
            border-top: 1px solid #f0f0f0; 
            margin-top: 80px;
        }
        footer h5 { font-weight: 800; color: #000; margin-bottom: 20px; }
        footer a { color: #666; text-decoration: none; transition: 0.2s; }
        footer a:hover { color: #000; }
        
        .social-icon {
            font-size: 1.5rem;
            margin-left: 15px;
            color: #333;
            transition: 0.2s;
        }
        .social-icon:hover { color: #000; transform: scale(1.1); }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand" href="/">PASO</a>
            
            <button class="navbar-toggler border-0 shadow-none" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item"><a class="nav-link" href="{% url 'home' %}">Inicio</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'marketplace' %}">Explorar</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'landing_businesses' %}">Negocios</a></li>
                    
                    {% if user.is_authenticated %}
                        <li class="nav-item ms-3">
                            <a class="btn btn-dark-paso" href="{% url 'dashboard_redirect' %}">Mi Panel</a>
                        </li>
                        <li class="nav-item ms-2">
                             <form action="{% url 'logout' %}" method="post" class="d-inline">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-link nav-link text-danger border-0 p-0 ms-2">
                                    <i class="bi bi-box-arrow-right fs-5"></i>
                                </button>
                            </form>
                        </li>
                    {% else %}
                        <li class="nav-item ms-3">
                            <a class="btn btn-outline-paso" href="{% url 'login' %}">Ingresar</a>
                        </li>
                        <li class="nav-item ms-2">
                            <a class="btn btn-dark-paso" href="{% url 'register_owner' %}">Crear Negocio</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main>
        {% block content %}
        {% endblock %}
    </main>

    <footer>
        <div class="container">
            <div class="row">
                <div class="col-md-5 mb-4">
                    <h5>PASO</h5>
                    <p class="text-muted small">
                        La plataforma definitiva para digitalizar tu negocio de belleza y bienestar.
                        Ahorra tiempo y crece sin límites.
                    </p>
                    <p class="text-muted small mt-3">
                        &copy; 2026 {{ global_settings.site_name|default:"Paso Ecosystem" }}. 
                        {{ global_settings.footer_text }}
                    </p>
                </div>
                
                <div class="col-md-2 mb-4">
                    <h6 class="fw-bold text-uppercase small mb-3">Plataforma</h6>
                    <ul class="list-unstyled small d-grid gap-2">
                        <li><a href="{% url 'marketplace' %}">Buscar Servicios</a></li>
                        <li><a href="{% url 'landing_businesses' %}">Para Negocios</a></li>
                        <li><a href="{% url 'login' %}">Iniciar Sesión</a></li>
                    </ul>
                </div>

                <div class="col-md-2 mb-4">
                    <h6 class="fw-bold text-uppercase small mb-3">Legal</h6>
                    <ul class="list-unstyled small d-grid gap-2">
                        <li><a href="#">Términos de Uso</a></li>
                        <li><a href="#">Privacidad</a></li>
                    </ul>
                </div>

                <div class="col-md-3 mb-4 text-md-end">
                    <h6 class="fw-bold text-uppercase small mb-3">Síguenos</h6>
                    <div class="d-flex justify-content-md-end">
                        {% if global_settings.instagram_link %}
                        <a href="{{ global_settings.instagram_link }}" target="_blank" class="social-icon">
                            <i class="bi bi-instagram"></i>
                        </a>
                        {% else %}
                        <a href="#" class="social-icon text-muted" title="Instagram no configurado"><i class="bi bi-instagram"></i></a>
                        {% endif %}

                        {% if global_settings.whatsapp_number %}
                        <a href="https://wa.me/{{ global_settings.whatsapp_number }}" target="_blank" class="social-icon">
                            <i class="bi bi-whatsapp"></i>
                        </a>
                        {% else %}
                        <a href="#" class="social-icon text-muted" title="WhatsApp no configurado"><i class="bi bi-whatsapp"></i></a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

def restaurar_conexion_y_diseno():
    print("🧠 Restaurando cerebro (Context Processors y Models)...")
    
    # 1. Crear carpeta core_saas si no existe (por seguridad)
    if not os.path.exists(CORE_APP_DIR):
        print("   ⚠️ Creando carpeta core_saas...")
        os.makedirs(CORE_APP_DIR)
        with open(os.path.join(CORE_APP_DIR, "__init__.py"), "w") as f: f.write("")

    # 2. Escribir Models
    with open(MODELS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_MODELS)

    # 3. Escribir Admin
    with open(ADMIN_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_ADMIN)

    # 4. Escribir Context Processor
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_CONTEXT)

    # 5. Escribir Master HTML (Diseño Blanco)
    print("🎨 Aplicando diseño BLANCO en Footer y conectando íconos...")
    with open(MASTER_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_MASTER)

    print("✅ ¡Sistema restaurado! Ahora el footer es blanco y lee la base de datos.")
    print("⚠️ IMPORTANTE: Asegúrate de que 'apps.core_saas.context_processors.global_settings' esté en tu settings.py en la sección TEMPLATES > OPTIONS > context_processors.")

if __name__ == "__main__":
    restaurar_conexion_y_diseno()