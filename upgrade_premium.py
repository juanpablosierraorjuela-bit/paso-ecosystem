import os
import subprocess

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_HTML = os.path.join(BASE_DIR, "templates", "base.html")
MARKET_HTML = os.path.join(BASE_DIR, "templates", "marketplace.html")

def upgrade_base_navbar():
    print("🛠️ Corrigiendo Logout y Navbar...")
    if not os.path.exists(BASE_HTML): return
    
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazo del botón de Logout simple por el formulario POST requerido por Django 5
    old_logout = '<a class="nav-link" href="{% url \'logout\' %}">Salir</a>'
    new_logout = """<form method="post" action="{% url 'logout' %}" class="d-inline">
                        {% csrf_token %}
                        <button type="submit" class="nav-link border-0 bg-transparent" style="cursor:pointer;">Salir</button>
                    </form>"""
    
    if old_logout in content:
        content = content.replace(old_logout, new_logout)
        with open(BASE_HTML, "w", encoding="utf-8") as f:
            f.write(content)

def upgrade_marketplace():
    print("💎 Rediseñando Marketplace a Estilo Premium...")
    
    premium_market = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h1 class="display-5 fw-bold text-dark">Ecosistema Premium</h1>
        <p class="lead text-muted">Descubre la excelencia en servicios empresariales.</p>
    </div>

    <div class="row g-4">
        {% for salon in salons %}
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm" style="border-radius: 15px; overflow: hidden; transition: transform 0.3s;">
                <div class="card-body text-center p-4">
                    <div class="mx-auto mb-3 d-flex align-items-center justify-content-center shadow-sm" 
                         style="width: 80px; height: 80px; background: linear-gradient(135deg, #1a1a1a 0%, #434343 100%); border-radius: 50%; border: 2px solid #d4af37;">
                        <span class="h2 mb-0 text-white fw-light" style="letter-spacing: 2px;">{{ salon.name|slice:":1"|upper }}</span>
                    </div>
                    
                    <h4 class="fw-bold text-dark mb-1">{{ salon.name }}</h4>
                    <p class="text-muted small mb-3"><i class="bi bi-geo-alt"></i> {{ salon.address|default:"Ubicación Premium" }}</p>
                    
                    <div class="d-flex justify-content-center gap-3 mb-4">
                        {% if salon.whatsapp %}
                        <a href="https://wa.me/{{ salon.whatsapp }}" target="_blank" class="text-success fs-5"><i class="bi bi-whatsapp"></i></a>
                        {% endif %}
                        {% if salon.instagram %}
                        <a href="https://instagram.com/{{ salon.instagram }}" target="_blank" class="text-danger fs-5"><i class="bi bi-instagram"></i></a>
                        {% endif %}
                        <a href="https://www.google.com/maps/search/{{ salon.address }}" target="_blank" class="text-primary fs-5"><i class="bi bi-map"></i></a>
                    </div>

                    <a href="{% url 'salon_detail' salon.id %}" class="btn btn-dark w-100 py-2 text-uppercase fw-bold small" style="letter-spacing: 1px; border-radius: 8px;">
                        Ver Portafolio
                    </a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<style>
    .card:hover { transform: translateY(-10px); }
</style>
{% endblock %}"""
    
    with open(MARKET_HTML, "w", encoding="utf-8") as f:
        f.write(premium_market)

def push_to_github():
    print("🚀 Subiendo cambios a GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Diseño Premium y fix de Logout"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ ¡Sincronizado con éxito!")
    except Exception as e:
        print(f"❌ Error en Git: {e}")

if __name__ == "__main__":
    upgrade_base_navbar()
    upgrade_marketplace()
    push_to_github()
    print("\n✨ Proceso terminado. Auto-destruyendo script...")
    os.remove(__file__)