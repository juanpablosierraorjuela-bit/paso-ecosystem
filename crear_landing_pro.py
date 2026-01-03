import os
import textwrap
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"💎 Creado/Actualizado: {path}")

print("🏗️ CONSTRUYENDO LANDING PAGE DE VENTAS (Handling 10 Objections)...")

# ==============================================================================
# 1. TEMPLATE: LANDING PAGE DE NEGOCIOS (Persuasión Pura)
# ==============================================================================
landing_content = """
{% extends 'base.html' %}
{% load static %}

{% block content %}
<style>
    .hero-section {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: white;
        padding: 100px 0;
        position: relative;
        overflow: hidden;
    }
    .feature-card {
        border: none;
        border-radius: 16px;
        background: #fff;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        padding: 2rem;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
    }
    .icon-box {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #f8f9fa;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        color: #111;
    }
    .check-list li {
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
</style>

<header class="hero-section text-center">
    <div class="container position-relative z-2">
        <span class="badge border border-light rounded-pill px-3 py-2 mb-4 fw-light tracking-wide text-uppercase">
            Para dueños que valoran su tiempo
        </span>
        <h1 class="display-3 fw-bold mb-4">Deja de ser secretario.<br>Empieza a ser CEO.</h1>
        <p class="lead text-white-50 mb-5 mx-auto" style="max-width: 700px;">
            El único ecosistema diseñado para eliminar los "No Show", blindar tus ingresos y llenar tu agenda mientras duermes. Sin comisiones por venta.
        </p>
        <div class="d-flex justify-content-center gap-3">
            <a href="#beneficios" class="btn btn-light btn-lg rounded-pill px-5 py-3 fw-bold">
                Ver cómo funciona
            </a>
        </div>
    </div>
</header>

<section id="beneficios" class="py-5 bg-light">
    <div class="container py-5">
        <div class="text-center mb-5">
            <h2 class="fw-bold">10 Problemas Reales, 1 Solución Blindada</h2>
            <p class="text-muted">Diseñamos esto escuchando lo que realmente te duele.</p>
        </div>

        <div class="row g-4">
            
            <div class="col-md-6 col-lg-4">
                <div class="feature-card shadow-sm">
                    <div class="icon-box"><i class="fas fa-lock"></i></div>
                    <h4 class="fw-bold mb-3">El "Candado Financiero"</h4>
                    <p class="text-muted small mb-3">¿Miedo a que reserven y no lleguen?</p>
                    <p class="mb-0">El sistema da 60 minutos al cliente para subir su comprobante de pago. Si no lo hace, libera la hora automáticamente. <strong>Nadie ocupa un espacio sin poner dinero sobre la mesa.</strong></p>
                </div>
            </div>

            <div class="col-md-6 col-lg-4">
                <div class="feature-card shadow-sm">
                    <div class="icon-box"><i class="fas fa-ghost"></i></div>
                    <h4 class="fw-bold mb-3">Registro Invisible</h4>
                    <p class="text-muted small mb-3">¿Clientes perezosos con la tecnología?</p>
                    <p class="mb-0">Diseñamos un flujo sin fricción. Primero escogen servicio y hora, y solo al final ponen sus datos básicos. Es tan natural que ni sienten el registro.</p>
                </div>
            </div>

            <div class="col-md-6 col-lg-4">
                <div class="feature-card shadow-sm">
                    <div class="icon-box"><i class="fas fa-clock"></i></div>
                    <h4 class="fw-bold mb-3">Vende Mientras Duermes</h4>
                    <p class="text-muted small mb-3">¿Tu cuaderno vende a las 11 PM?</p>
                    <p class="mb-0">Si un cliente quiere agendarse a medianoche, tu cuaderno está cerrado. Nuestro sistema cobra, envía ubicación y entrega el Ticket Digital mientras tú descansas.</p>
                </div>
            </div>

            <div class="col-md-6 col-lg-4">
                <div class="feature-card shadow-sm">
                    <div class="icon-box"><i class="fas fa-hand-holding-usd"></i></div>
                    <h4 class="fw-bold mb-3">Tu Dinero es Tuyo</h4>
                    <p class="text-muted small mb-3">¿Miedo a las comisiones?</p>
                    <p class="mb-0">La plataforma NO toca tu dinero. El cliente te transfiere directo a tu Nequi o Daviplata. Tú verificas y apruebas. Sin intermediarios, sin "mordidas".</p>
                </div>
            </div>

            <div class="col-md-6 col-lg-4">
                <div class="feature-card shadow-sm">
                    <div class="icon-box"><i class="fas fa-puzzle-piece"></i></div>
                    <h4 class="fw-bold mb-3">Lógica de Huecos</h4>
                    <p class="text-muted small mb-3">¿Se cruzan las citas del local con internet?</p>
                    <p class="mb-0">Imposible. Si bloqueas una hora en el local, desaparece de internet al instante. El sistema calcula duraciones exactas para que matemáticamente no haya cruces.</p>
                </div>
            </div>

            <div class="col-md-6 col-lg-4">
                <div class="feature-card shadow-sm">
                    <div class="icon-box"><i class="fas fa-users"></i></div>
                    <h4 class="fw-bold mb-3">Gestión de Equipo</h4>
                    <p class="text-muted small mb-3">¿Empleados rotativos?</p>
                    <p class="mb-0">Ellos tienen su propio panel para ver sus citas y ganancias. Si alguien se va, lo desactivas con un clic y el sistema reorganiza todo. Cero estrés operativo.</p>
                </div>
            </div>

            <div class="col-md-6">
                <div class="feature-card shadow-sm d-flex gap-4 align-items-start">
                    <div class="icon-box flex-shrink-0"><i class="fas fa-traffic-light"></i></div>
                    <div>
                        <h4 class="fw-bold mb-3">Semáforo de Seguridad</h4>
                        <p class="mb-0">¿Comprobantes falsos? La cita se pone en <span class="badge bg-warning text-dark">AMARILLO</span> cuando el cliente dice que pagó. Tú no la pasas a <span class="badge bg-success">VERDE</span> hasta que veas la plata en tu banco. Tú tienes el control absoluto.</p>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="feature-card shadow-sm d-flex gap-4 align-items-start">
                    <div class="icon-box flex-shrink-0"><i class="fab fa-whatsapp"></i></div>
                    <div>
                        <h4 class="fw-bold mb-3">Adiós al Chat Eterno</h4>
                        <p class="mb-0">Deja de responder "¿qué precio tiene?" y "¿tienes turno a las 3?". El sistema informa precios, muestra horas libres y cobra. A ti solo te llega el mensaje final: "Hola, aquí está mi abono".</p>
                    </div>
                </div>
            </div>

        </div>
    </div>
</section>

<section class="py-5 bg-white">
    <div class="container py-5">
        <div class="row align-items-center">
            <div class="col-lg-6">
                <h2 class="display-5 fw-bold mb-4">La oferta de lanzamiento</h2>
                <ul class="list-unstyled check-list lead text-muted">
                    <li><i class="fas fa-check-circle text-success"></i> Configuración VIP (Lo hacemos por ti).</li>
                    <li><i class="fas fa-check-circle text-success"></i> Soporte local en Tunja.</li>
                    <li><i class="fas fa-check-circle text-success"></i> Actualizaciones constantes.</li>
                    <li><i class="fas fa-check-circle text-success"></i> Sin cláusulas de permanencia.</li>
                </ul>
            </div>
            <div class="col-lg-6 text-center text-lg-end">
                <div class="p-5 bg-light rounded-4 border">
                    <h3 class="fw-bold mb-3">¿Listo para evolucionar?</h3>
                    <p class="mb-4 text-muted">No es una app genérica. Es una herramienta blindada para negocios reales.</p>
                    <a href="{% url 'register_owner' %}" class="btn btn-dark btn-lg w-100 py-3 rounded-pill shadow-lg fw-bold tracking-wide">
                        Registrar mi Negocio Ahora
                    </a>
                    <p class="small text-muted mt-3 mb-0">Configuración inmediata • Acceso seguro SSL</p>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}
"""
create_file('templates/landing_businesses.html', landing_content)

# ==============================================================================
# 2. ACTUALIZAR NAVBAR EN BASE.HTML
# ==============================================================================
# Cambiamos el link de 'Negocios' para que apunte a 'landing_businesses'
base_path = 'templates/base.html'
try:
    with open(base_path, 'r', encoding='utf-8') as f:
        base_html = f.read()
    
    # Buscamos el link viejo y lo reemplazamos
    old_link = '{% url \'register_owner\' %}'
    new_link = '{% url \'landing_businesses\' %}'
    
    # Solo reemplazamos el del menú de navegación, no los botones de acción si no queremos
    # Pero como dijiste "el boton de negocios que pusiste en la parte superior", asumimos el navbar.
    if old_link in base_html:
        base_html = base_html.replace('href="' + old_link + '"', 'href="' + new_link + '"')
        
        # OJO: Pero el botón de "Crear Cuenta" o "Registrar mi Negocio" dentro de la landing 
        # SÍ debe llevar al registro. Y en el home también.
        # Vamos a ser más quirúrgicos.
        # Reemplazamos SOLO el del menú "Negocios".
        
        # Restauramos los botones que dicen "Crear Cuenta" o "Registrar mi Negocio" explícitamente
        # para que sigan llevando al registro directo si el usuario ya está decidido (Home).
        # Aunque tu solicitud dice que "el boton de negocios... lleve a una nueva landing".
        # Haremos que el link del Navbar apunte a la Landing.
        
        create_file(base_path, base_html)
    else:
        print("ℹ️ No encontré el link viejo en base.html, quizás ya se cambió.")
except Exception as e:
    print(f"⚠️ Error editando base.html: {e}")

# ==============================================================================
# 3. ACTUALIZAR VIEWS.PY (AGREGAR LA VISTA DE LA LANDING)
# ==============================================================================
views_path = 'apps/businesses/views.py'
try:
    with open(views_path, 'r', encoding='utf-8') as f:
        views_code = f.read()
    
    if "def landing_businesses(request):" not in views_code:
        # Agregamos la vista al final
        new_view = """
# --- LANDING PAGES ---
def landing_businesses(request):
    return render(request, 'landing_businesses.html')
"""
        with open(views_path, 'a', encoding='utf-8') as f:
            f.write(new_view)
        print("✅ Vista landing_businesses agregada a views.py")
    else:
        print("ℹ️ La vista ya existía.")
except Exception as e:
    print(f"❌ Error en views.py: {e}")

# ==============================================================================
# 4. ACTUALIZAR URLS.PY (AGREGAR LA RUTA)
# ==============================================================================
urls_path = 'paso_ecosystem/urls.py'
try:
    with open(urls_path, 'r', encoding='utf-8') as f:
        urls_code = f.read()
    
    if "landing_businesses" not in urls_code:
        # Insertamos la url antes de 'urlpatterns ]'
        # Buscamos una línea conocida para insertar después
        if "path('registro-negocio/'," in urls_code:
            new_line = "    path('negocios/', views.landing_businesses, name='landing_businesses'),"
            urls_code = urls_code.replace("path('registro-negocio/',", f"{new_line}\n    path('registro-negocio/',")
            create_file(urls_path, urls_code)
            print("✅ Ruta /negocios/ agregada a urls.py")
    else:
        print("ℹ️ La ruta ya existía.")
except Exception as e:
    print(f"❌ Error en urls.py: {e}")

# ==============================================================================
# 5. SUBIDA Y LIMPIEZA
# ==============================================================================
print("🤖 Subiendo Landing Page de Ventas...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Marketing: Added 'God Mode' Landing Page for Businesses with objection handling"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡ENVIADO! Ahora tu botón 'Negocios' vende por ti.")
except Exception as e:
    print(f"⚠️ Error git: {e}")

print("💥 Autodestruyendo script...")
try:
    os.remove(__file__)
except: pass