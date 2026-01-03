import os
import sys

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTER_HTML = os.path.join(BASE_DIR, "templates", "registration", "register_owner.html")
LOGIN_HTML = os.path.join(BASE_DIR, "templates", "registration", "login.html")

# --- NUEVO DISEÑO: "BLACK & WHITE BUSINESS PREMIUM" ---

# 1. REGISTRO (Sin azul, todo en escala de grises y negro elegante)
CONTENIDO_REGISTER = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="text-center mb-5">
                <h1 class="display-5 fw-bold text-dark">Ecosistema PASO</h1>
                <p class="lead text-muted">Registro Empresarial</p>
            </div>

            <form method="post" class="needs-validation" novalidate>
                {% csrf_token %}
                
                <div class="card shadow-sm border-0 mb-4" style="background-color: #f8f9fa;">
                    <div class="card-body p-5">
                        <div class="d-flex align-items-center mb-4 border-bottom pb-3">
                            <div class="bg-dark text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                <i class="bi bi-person-fill"></i>
                            </div>
                            <h3 class="h4 mb-0 text-dark">Datos del Administrador</h3>
                        </div>
                        
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Nombre</label>
                                {{ user_form.first_name }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Apellido</label>
                                {{ user_form.last_name }}
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Correo Profesional</label>
                                {{ user_form.email }}
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Usuario de Acceso</label>
                                {{ user_form.username }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Contraseña</label>
                                {{ user_form.password }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Confirmar Contraseña</label>
                                {{ user_form.password_confirm }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card shadow border-0 mb-5">
                    <div class="card-body p-5">
                        <div class="d-flex align-items-center mb-4 border-bottom pb-3">
                            <div class="bg-dark text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                <i class="bi bi-building"></i>
                            </div>
                            <h3 class="h4 mb-0 text-dark">Información del Negocio</h3>
                        </div>

                        <div class="row g-3">
                            <div class="col-12">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Nombre Comercial</label>
                                {{ salon_form.name }}
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Dirección Física</label>
                                {{ salon_form.address }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-secondary small text-uppercase">Teléfono</label>
                                {{ salon_form.phone }}
                            </div>
                            
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-secondary small text-uppercase"><i class="bi bi-whatsapp"></i> WhatsApp Business</label>
                                <div class="input-group">
                                    <span class="input-group-text bg-light border text-muted">+</span>
                                    {{ salon_form.whatsapp }}
                                </div>
                            </div>
                            
                            <div class="col-md-12">
                                <label class="form-label fw-bold text-secondary small text-uppercase"><i class="bi bi-instagram"></i> Instagram</label>
                                <div class="input-group">
                                    <span class="input-group-text bg-light border text-muted">@</span>
                                    {{ salon_form.instagram }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="d-grid gap-2 mb-5">
                    <button type="submit" class="btn btn-dark btn-lg py-3 fw-bold text-uppercase" style="letter-spacing: 1px;">
                        Completar Registro
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""

# 2. LOGIN (Fondo oscuro elegante a la izquierda, formulario limpio a la derecha)
CONTENIDO_LOGIN = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container d-flex align-items-center justify-content-center" style="min-height: 85vh;">
    <div class="card shadow-lg border-0 rounded-0 overflow-hidden" style="max-width: 1000px; width: 100%;">
        <div class="row g-0">
            <div class="col-md-6 bg-dark d-none d-md-flex align-items-center justify-content-center text-white p-5">
                <div class="text-center">
                    <div class="mb-4">
                         <i class="bi bi-gem display-4"></i>
                    </div>
                    <h2 class="fw-light text-uppercase tracking-wider mb-3">Bienvenido</h2>
                    <p class="text-white-50 lead fs-6">Gestión inteligente para negocios de alto nivel.</p>
                </div>
            </div>

            <div class="col-md-6 p-5 bg-white">
                <div class="text-center mb-5">
                    <h3 class="fw-bold text-dark text-uppercase small" style="letter-spacing: 2px;">Iniciar Sesión</h3>
                </div>

                <form method="post">
                    {% csrf_token %}
                    
                    {% if form.errors %}
                        <div class="alert alert-dark py-2 small rounded-0 mb-4" role="alert">
                            Credenciales incorrectas.
                        </div>
                    {% endif %}

                    <div class="form-floating mb-3">
                        <input type="text" name="username" class="form-control border-0 border-bottom rounded-0 ps-0" id="floatingInput" placeholder="Usuario" required style="box-shadow: none; border-color: #333;">
                        <label for="floatingInput" class="ps-0 text-muted">Usuario</label>
                    </div>
                    
                    <div class="form-floating mb-5">
                        <input type="password" name="password" class="form-control border-0 border-bottom rounded-0 ps-0" id="floatingPassword" placeholder="Contraseña" required style="box-shadow: none; border-color: #333;">
                        <label for="floatingPassword" class="ps-0 text-muted">Contraseña</label>
                    </div>

                    <div class="d-grid mb-4">
                        <button type="submit" class="btn btn-dark rounded-0 py-3 text-uppercase fw-bold" style="letter-spacing: 2px;">Ingresar</button>
                    </div>

                    <div class="text-center mt-4">
                        <p class="small text-muted">¿No tienes cuenta? <a href="{% url 'register_owner' %}" class="text-dark fw-bold text-decoration-none">Regístrate aquí</a></p>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def aplicar_estilo_elegante():
    print("🎨 Aplicando diseño 'Business Elegant'...")
    
    # Escribir Registro
    with open(REGISTER_HTML, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_REGISTER)
    print("   -> Registro actualizado: Estilo sobrio, tarjetas limpias, sin azul chillón.")

    # Escribir Login
    with open(LOGIN_HTML, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_LOGIN)
    print("   -> Login actualizado: Fondo negro/blanco, inputs minimalistas, botones oscuros.")

if __name__ == "__main__":
    aplicar_estilo_elegante()
    print("\n✅ ¡Diseño actualizado! Ahora se ve como una plataforma profesional.")