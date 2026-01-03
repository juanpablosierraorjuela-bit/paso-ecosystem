import os
import textwrap
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"💎 Diseño Actualizado: {path}")

print("✨ INICIANDO PROTOCOLO DE DISEÑO PREMIUM (Mobile & Desktop)...")

# ==============================================================================
# 1. BASE.HTML (MENÚ MEJORADO Y RESPONSIVE)
# ==============================================================================
# Cambios:
# - Agregado enlace "Explorar" visible siempre.
# - Tipografía 'Inter' optimizada.
# - Menú móvil colapsable más elegante.
# - Footer minimalista pero completo.
base_content = """
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paso Marketplace | Tu Belleza, Tu Tiempo</title>
    
    <link rel="icon" type="image/svg+xml" href="{% static 'images/favicon.svg' %}">
    <link rel="apple-touch-icon" href="{% static 'images/favicon.svg' %}">
    <meta name="theme-color" content="#ffffff">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <style>
        /* ESTILO GLOBAL DE LUJO MINIMALISTA */
        :root {
            --bs-font-sans-serif: 'Inter', system-ui, -apple-system, sans-serif;
            --bs-body-bg: #ffffff;
            --bs-body-color: #1a1a1a;
        }
        
        body { 
            font-family: var(--bs-font-sans-serif); 
            -webkit-font-smoothing: antialiased; 
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        
        /* Navbar Premium */
        .navbar {
            padding: 1.2rem 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        .navbar-brand { 
            font-weight: 800; 
            font-size: 1.6rem; 
            letter-spacing: -1px; 
            color: #000 !important; 
        }
        .nav-link {
            font-weight: 500;
            color: #555 !important;
            font-size: 0.95rem;
            margin: 0 0.5rem;
            transition: color 0.2s;
        }
        .nav-link:hover { color: #000 !important; }
        
        /* Botones Personalizados */
        .btn-dark {
            background-color: #111;
            border: 1px solid #111;
            padding: 0.6rem 1.4rem;
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.3px;
            transition: all 0.3s ease;
        }
        .btn-dark:hover {
            background-color: #333;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .btn-outline-dark {
            border: 1px solid #e0e0e0;
            color: #111;
            padding: 0.6rem 1.4rem;
            border-radius: 8px;
            font-weight: 600;
        }
        .btn-outline-dark:hover {
            background-color: #f8f9fa;
            border-color: #111;
            color: #000;
        }

        /* Tarjetas */
        .card { 
            border: 1px solid rgba(0,0,0,0.05); 
            border-radius: 16px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.02); 
            transition: transform 0.3s ease, box-shadow 0.3s ease; 
        }
        .card:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 12px 24px rgba(0,0,0,0.06); 
        }
        
        /* Utilidades */
        .tracking-wide { letter-spacing: 0.05em; }
        .text-gradient {
            background: linear-gradient(135deg, #111 0%, #555 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg fixed-top">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center gap-2" href="{% url 'home' %}">
                <img src="{% static 'images/favicon.svg' %}" width="32" height="32" alt="P">
                PASO.
            </a>
            
            <button class="navbar-toggler border-0 p-0 shadow-none" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarMain">
                <ul class="navbar-nav mx-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'marketplace' %}">Explorar</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'register_owner' %}">Negocios</a>
                    </li>
                </ul>
                
                <div class="d-flex align-items-center gap-3 mt-3 mt-lg-0">
                    {% if user.is_authenticated %}
                        {% if is_owner %}
                            <a href="{% url 'owner_dashboard' %}" class="btn btn-dark btn-sm">Mi Panel</a>
                        {% else %}
                            <a href="{% url 'client_dashboard' %}" class="btn btn-dark btn-sm">Mis Citas</a>
                        {% endif %}
                        <a href="{% url 'saas_logout' %}" class="text-muted text-decoration-none small fw-bold px-2">Salir</a>
                    {% else %}
                        <a href="{% url 'saas_login' %}" class="fw-bold text-dark text-decoration-none me-2">Entrar</a>
                        <a href="{% url 'register_owner' %}" class="btn btn-dark btn-sm">Crear Cuenta</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <div style="height: 80px;"></div>

    <main class="flex-grow-1">
        {% if messages %}
            <div class="container mt-4">
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show border-0 shadow-sm rounded-3">
                        <i class="fas fa-info-circle me-2"></i> {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    <footer class="bg-white py-5 mt-5 border-top">
        <div class="container">
            <div class="row gy-4 justify-content-between align-items-center">
                <div class="col-md-4 text-center text-md-start">
                    <h5 class="fw-bold mb-1">PASO.</h5>
                    <p class="text-muted small mb-0">Ecosistema digital de belleza.</p>
                </div>
                <div class="col-md-4 text-center">
                    <small class="text-muted">&copy; 2026 Paso Ecosystem.</small>
                </div>
                <div class="col-md-4 text-center text-md-end">
                    <a href="#" class="text-muted me-3"><i class="fab fa-instagram"></i></a>
                    <a href="#" class="text-muted"><i class="fab fa-whatsapp"></i></a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
create_file('templates/base.html', base_content)

# ==============================================================================
# 2. HOME.HTML (CENTRADO PERFECTO Y DISEÑO LIMPIO)
# ==============================================================================
# Cambios:
# - Se usa 'min-vh-100' y flexbox para centrar verticalmente de verdad.
# - Botones responsivos (columnas en móvil, fila en desktop).
# - Texto más elegante y separado.
home_content = """
{% extends 'base.html' %}
{% block content %}
<div class="container">
    <div class="row align-items-center justify-content-center" style="min-height: 80vh;">
        <div class="col-lg-8 text-center">
            
            <div class="mb-4">
                <span class="badge bg-light text-dark border rounded-pill px-3 py-2 mb-3 tracking-wide fw-bold">
                    🚀 El futuro de la belleza
                </span>
            </div>

            <h1 class="display-3 fw-bold mb-4 lh-sm text-gradient" style="letter-spacing: -2px;">
                Tu estilo, tu tiempo,<br>
                <span class="text-dark">en un solo lugar.</span>
            </h1>
            
            <p class="lead text-muted mb-5 mx-auto" style="max-width: 600px; font-weight: 400;">
                Reserva en los mejores salones, barberías y spas de tu ciudad sin llamadas ni esperas. 
                Simple, rápido y exclusivo.
            </p>

            <div class="d-flex flex-column flex-sm-row gap-3 justify-content-center">
                <a href="{% url 'marketplace' %}" class="btn btn-dark btn-lg px-5 py-3 shadow-lg rounded-pill">
                    <i class="fas fa-search me-2"></i> Buscar Servicios
                </a>
                <a href="{% url 'register_owner' %}" class="btn btn-outline-dark btn-lg px-5 py-3 rounded-pill">
                    Registrar mi Negocio
                </a>
            </div>

            <div class="row mt-5 pt-4 g-4 justify-content-center text-muted small">
                <div class="col-auto d-flex align-items-center gap-2">
                    <i class="fas fa-check-circle text-success"></i> Reserva 24/7
                </div>
                <div class="col-auto d-flex align-items-center gap-2">
                    <i class="fas fa-shield-alt text-success"></i> Pagos Seguros
                </div>
                <div class="col-auto d-flex align-items-center gap-2">
                    <i class="fas fa-bolt text-success"></i> Confirmación Inmediata
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
create_file('templates/home.html', home_content)

# ==============================================================================
# 3. SUBIDA AUTOMÁTICA Y LIMPIEZA
# ==============================================================================
print("🤖 Subiendo actualización visual a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Design: UX Upgrade - Centered Home, Responsive Nav, Luxury UI"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡ENVIADO! En 2 minutos verás el cambio radical.")
except Exception as e:
    print(f"⚠️ Error git: {e}")

print("💥 Autodestruyendo script de diseño...")
try:
    os.remove(__file__)
    print("🧹 Script eliminado. Tu carpeta sigue limpia.")
except: pass