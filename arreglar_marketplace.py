import os

# ==========================================
# NUEVO DISEÑO PARA EL MARKETPLACE (home.html)
# ==========================================
# Incluye el bloque "Sin Resultados" con las opciones de Unirse o Recomendar.

HOME_HTML_CONTENT = """
{% extends 'base_saas.html' %}
{% load static %}

{% block content %}
<div class="container py-4">
    
    <div class="row mb-5 justify-content-center">
        <div class="col-lg-8">
            <div class="glass-panel p-2 rounded-pill shadow-sm d-flex align-items-center">
                <form action="{% url 'marketplace' %}" method="get" class="w-100 d-flex">
                    <input type="hidden" name="lat" value="{{ request.GET.lat }}">
                    <input type="hidden" name="lng" value="{{ request.GET.lng }}">
                    
                    <input type="text" name="q" class="form-control border-0 bg-transparent ps-4" 
                           placeholder="¿Qué salón o servicio buscas hoy?" 
                           value="{{ request.GET.q|default:'' }}" 
                           style="box-shadow: none;">
                    
                    <button type="submit" class="btn btn-primary rounded-pill px-4 ms-2">
                        <i class="fas fa-search"></i>
                    </button>
                </form>
            </div>
            
            {% if user_located %}
            <div class="text-center mt-2">
                <small class="text-muted">
                    <i class="fas fa-map-marker-alt text-danger me-1"></i> 
                    Resultados basados en tu ubicación actual
                    <a href="{% url 'marketplace' %}" class="text-dark fw-bold ms-1" style="text-decoration: underline;">Ver todo el país</a>
                </small>
            </div>
            {% endif %}
        </div>
    </div>

    <div class="row g-4">
        {% for salon in salones %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 border-0 shadow-sm glass-panel overflow-hidden hover-scale">
                    <div class="position-relative" style="height: 200px; background-color: #eee;">
                        {% if salon.cover_image %}
                            <img src="{{ salon.cover_image.url }}" class="w-100 h-100 object-fit-cover" alt="{{ salon.name }}">
                        {% else %}
                            <div class="d-flex align-items-center justify-content-center h-100 bg-secondary text-white">
                                <i class="fas fa-store fa-3x opacity-50"></i>
                            </div>
                        {% endif %}
                        
                        <div class="position-absolute top-0 end-0 m-3">
                            {% if salon.is_open_now_dynamic %}
                                <span class="badge bg-success shadow-sm">Abierto Ahora</span>
                            {% else %}
                                <span class="badge bg-secondary shadow-sm">Cerrado</span>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="card-body">
                        <h5 class="card-title fw-bold font-heading mb-1">{{ salon.name }}</h5>
                        <p class="text-muted small mb-3">
                            <i class="fas fa-map-pin me-1"></i> {{ salon.city|default:"Ubicación no especificada" }}
                        </p>
                        
                        <div class="d-flex align-items-center justify-content-between mt-3">
                            <div class="d-flex align-items-center text-warning small">
                                <i class="fas fa-star me-1"></i>
                                <span class="fw-bold text-dark">5.0</span>
                                <span class="text-muted ms-1">(Nuevo)</span>
                            </div>
                            <a href="{% url 'booking_create' salon.slug %}" class="btn btn-outline-dark btn-sm rounded-pill px-3">
                                Reservar
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        
        {% empty %}
            <div class="col-12 text-center py-5">
                <div class="glass-panel p-5 d-inline-block" style="max-width: 700px;">
                    <div class="mb-4">
                        <div class="bg-light rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 80px; height: 80px;">
                            <i class="fas fa-map-marked-alt text-muted fa-3x"></i>
                        </div>
                    </div>
                    
                    <h2 class="font-heading fw-bold mb-3">¡Aún no hemos llegado a esta zona!</h2>
                    <p class="text-muted lead mb-4">
                        Actualmente no tenemos salones registrados cerca de tu ubicación. <br>
                        Pero tú puedes cambiar eso.
                    </p>

                    <div class="d-flex flex-column flex-md-row gap-3 justify-content-center">
                        <a href="{% url 'registro_owner' %}" class="btn btn-primary btn-lg rounded-pill px-5 shadow hover-lift">
                            <i class="fas fa-store me-2"></i> Soy un Salón y quiero unirme
                        </a>
                        
                        <a href="https://wa.me/?text=%C2%A1Hola!%20Te%20recomiendo%20unirte%20a%20PASO%20Ecosistem%20para%20gestionar%20tu%20sal%C3%B3n.%20Aqu%C3%AD%20est%C3%A1%20el%20link:%20https://paso-ecosystem.onrender.com/" 
                           target="_blank" 
                           class="btn btn-outline-dark btn-lg rounded-pill px-5 hover-lift">
                            <i class="fab fa-whatsapp me-2"></i> Recomendar a mi estilista
                        </a>
                    </div>
                    
                    <div class="mt-4 pt-3 border-top">
                        <a href="{% url 'marketplace' %}" class="text-muted small text-decoration-none">
                            <i class="fas fa-arrow-left me-1"></i> Ver salones en otras ciudades
                        </a>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
</div>

<style>
    .hover-scale:hover { transform: translateY(-5px); transition: all 0.3s ease; }
    .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important; transition: all 0.3s ease; }
    .object-fit-cover { object-fit: cover; }
    /* Ajuste para que el input de búsqueda no tenga borde azul al hacer clic */
    .form-control:focus { box-shadow: none; border-color: transparent; }
</style>
{% endblock %}
"""

def arreglar_template():
    base_dir = os.getcwd()
    path_template = os.path.join(base_dir, 'templates', 'home.html')
    
    print(f"🛠️  Actualizando {path_template}...")
    with open(path_template, 'w', encoding='utf-8') as f:
        f.write(HOME_HTML_CONTENT)
        
    print("✅  ¡Listo! El Marketplace ahora maneja ubicaciones vacías elegantemente.")
    print("👉  Ejecuta: python subir_cambios.py (o git add/commit/push) para ver los cambios en Render.")

if __name__ == "__main__":
    arreglar_template()