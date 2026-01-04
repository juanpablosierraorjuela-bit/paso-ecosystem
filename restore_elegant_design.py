import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
MASTER_HTML_PATH = os.path.join(TEMPLATES_DIR, "master.html")

# --- CONTENIDO DE MASTER.HTML (DISEÑO ELEGANTE Y SOBRIO) ---
CONTENIDO_MASTER = """{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PASO | Tu Negocio, Tu Tiempo</title>
    
    <link rel="icon" type="image/png" href="{% static 'img/favicon.ico' %}">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;900&display=swap" rel="stylesheet">
    
    <style>
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: #ffffff; 
            color: #000;
            display: flex; 
            flex-direction: column; 
            min-height: 100vh; 
        }
        
        /* NAVBAR ELEGANTE */
        .navbar { 
            background-color: #ffffff; 
            padding: 20px 0; 
            border-bottom: 1px solid #f0f0f0;
        }
        .navbar-brand { 
            font-weight: 900; 
            font-size: 1.5rem; 
            letter-spacing: -1px; 
            color: #000 !important; 
        }
        .nav-link { 
            font-weight: 500; 
            color: #666 !important; 
            margin-left: 15px; 
            transition: 0.2s; 
            font-size: 0.95rem;
        }
        .nav-link:hover { 
            color: #000 !important; 
        }
        
        /* BOTONES SOBRIOS */
        .btn-black { 
            background-color: #000; 
            color: #fff; 
            border: 1px solid #000;
            padding: 8px 24px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: 0.3s;
        }
        .btn-black:hover { 
            background-color: #333; 
            color: #fff;
        }
        .btn-outline-black { 
            background-color: transparent; 
            color: #000; 
            border: 1px solid #e0e0e0;
            padding: 8px 24px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: 0.3s;
        }
        .btn-outline-black:hover { 
            border-color: #000;
        }

        /* CONTENIDO */
        main { flex: 1; }

        /* FOOTER MINIMALISTA */
        footer { 
            background-color: #000; 
            color: #fff; 
            padding: 60px 0; 
            margin-top: auto; 
        }
        footer h5 { font-weight: 900; letter-spacing: -0.5px; }
        footer a { color: #999; text-decoration: none; transition: 0.2s; }
        footer a:hover { color: #fff; }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand" href="/">PASO</a>
            
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'home' %}">Inicio</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'marketplace' %}">Explorar</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'landing_businesses' %}">Negocios</a>
                    </li>
                    
                    {% if user.is_authenticated %}
                        <li class="nav-item ms-3">
                            <a class="btn btn-black rounded-pill" href="{% url 'dashboard_redirect' %}">
                                Ir al Panel
                            </a>
                        </li>
                        <li class="nav-item ms-2">
                             <form action="{% url 'logout' %}" method="post" class="d-inline">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-link nav-link text-secondary" style="text-decoration:none;">
                                    Salir
                                </button>
                            </form>
                        </li>
                    {% else %}
                        <li class="nav-item ms-3">
                            <a class="btn btn-outline-black rounded-pill" href="{% url 'login' %}">Ingresar</a>
                        </li>
                        <li class="nav-item ms-2">
                            <a class="btn btn-black rounded-pill" href="{% url 'register_owner' %}">
                                Comenzar
                            </a>
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
                <div class="col-md-4 mb-4">
                    <h5>PASO</h5>
                    <p class="text-white-50 small">Gestión inteligente para negocios modernos.</p>
                </div>
                <div class="col-md-4 mb-4">
                    </div>
                <div class="col-md-4 mb-4 text-md-end">
                    <a href="#" class="me-3"><i class="bi bi-instagram"></i></a>
                    <a href="#"><i class="bi bi-whatsapp"></i></a>
                    <p class="text-white-50 small mt-3">&copy; 2026 Paso Ecosystem</p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

def restaurar_diseno_elegante():
    print("🎩 Aplicando diseño 'All Black'...")
    print("   - Eliminando amarillo.")
    print("   - Restaurando logo PASO limpio.")
    print("   - Insertando Favicon.")
    
    with open(MASTER_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_MASTER)
        
    print("✅ ¡Diseño restaurado con éxito! Elegancia pura.")

if __name__ == "__main__":
    restaurar_diseno_elegante()