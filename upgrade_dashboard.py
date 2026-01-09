import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. LA BARRA DE NAVEGACIÓN (NAVBAR)
# ==========================================
base_html_content = """
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PASO Ecosistema</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Lato', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 font-sans flex flex-col min-h-screen text-gray-900">

    <nav class="bg-black text-white py-4 shadow-lg sticky top-0 z-50">
        <div class="container mx-auto px-4 flex justify-between items-center">
            <a href="/" class="text-2xl font-serif font-bold text-gold-500 tracking-wider hover:text-gray-300 transition">
                PASO
            </a>

            <div class="flex items-center space-x-6 text-sm font-bold">
                <a href="/marketplace/" class="hover:text-yellow-400 transition">MARKETPLACE</a>
                
                {% if user.is_authenticated %}
                    <span class="text-gray-500 hidden md:inline">Hola, {{ user.first_name }}</span>
                    
                    {% if user.role == 'OWNER' %}
                        <a href="{% url 'dashboard' %}" class="bg-white text-black px-4 py-2 rounded-full hover:bg-gray-200 transition">
                            MI PANEL
                        </a>
                    {% endif %}
                    
                    <form action="{% url 'logout' %}" method="post" class="inline">
                        {% csrf_token %}
                        <button type="submit" class="text-red-400 hover:text-red-300 ml-2">SALIR</button>
                    </form>
                {% else %}
                    <a href="{% url 'register_owner' %}" class="hidden md:inline hover:text-white text-gray-400">Soy Dueño</a>
                    <a href="{% url 'login' %}" class="bg-white text-black px-5 py-2 rounded-full hover:bg-gray-200 transition">
                        ENTRAR
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>

    <main class="flex-grow">
        {% if messages %}
            <div class="max-w-4xl mx-auto mt-4 px-4">
                {% for message in messages %}
                    <div class="p-4 rounded-lg shadow-md mb-2 text-white {% if message.tags == 'success' %}bg-green-600{% elif message.tags == 'error' %}bg-red-600{% else %}bg-blue-600{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    <footer class="bg-black text-white py-8 mt-12 border-t border-gray-900">
        <div class="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
            <div class="mb-4 md:mb-0">
                <p class="text-lg font-serif font-bold">PASO ECOSISTEMA</p>
                <p class="text-xs text-gray-500">Transformando la belleza en Colombia.</p>
            </div>
            <div class="text-xs text-gray-600">
                &copy; 2026 - Todos los derechos reservados
            </div>
            <div class="flex space-x-4 mt-4 md:mt-0">
                {% if global_settings.instagram_url %}
                    <a href="{{ global_settings.instagram_url }}" target="_blank" class="text-gray-400 hover:text-pink-500 transition">IG</a>
                {% endif %}
                <a href="#" class="text-gray-400 hover:text-blue-500 transition">FB</a>
            </div>
        </div>
    </footer>

</body>
</html>
"""

# ==========================================
# 2. LOGICA DEL DASHBOARD (VIEWS.PY)
# ==========================================
views_dashboard_content = """
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings

@login_required
def owner_dashboard(request):
    # Seguridad: Solo dueños
    if request.user.role != 'OWNER':
        return redirect('home')
    
    # Obtener Salón
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner') # Si por error no tiene salón

    # Lógica del Temporizador (The Reaper)
    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = int(remaining_time.total_seconds())
    
    if total_seconds_left < 0:
        total_seconds_left = 0

    # Lógica de WhatsApp
    admin_settings = GlobalSettings.objects.first()
    admin_phone = admin_settings.whatsapp_support if admin_settings else '573000000000' # Fallback
    
    wa_message = f"Hola PASO, quiero activar mi ecosistema. Soy el Negocio: {salon.name} (ID Usuario: {request.user.id}). Adjunto mi comprobante de $50.000."
    wa_link = f"https://wa.me/{admin_phone}?text={wa_message}"

    context = {
        'salon': salon,
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment
    }
    return render(request, 'businesses/dashboard.html', context)

# --- Vistas Placeholder para el futuro (Evita errores 404) ---
@login_required
def services_list(request):
    return render(request, 'base.html', {'content': 'Gestión de Servicios - Próximamente'})

@login_required
def employees_list(request):
    return render(request, 'base.html', {'content': 'Gestión de Empleados - Próximamente'})
"""

# ==========================================
# 3. HTML DEL DASHBOARD (CON JAVASCRIPT)
# ==========================================
html_dashboard_content = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">

    <div class="flex justify-between items-end mb-8 border-b pb-4">
        <div>
            <h1 class="text-4xl font-serif text-gray-900">{{ salon.name }}</h1>
            <p class="text-gray-500">Panel de Control &bull; {{ salon.city }}</p>
        </div>
        <div>
            <span class="bg-gray-100 text-gray-800 text-xs font-semibold px-2.5 py-0.5 rounded border border-gray-500">
                {% if is_trial %}MODO PRUEBA{% else %}PREMIUM{% endif %}
            </span>
        </div>
    </div>

    {% if is_trial %}
    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-6 mb-8 rounded-r-lg shadow-sm relative overflow-hidden">
        <div class="flex items-start z-10 relative">
            <div class="flex-shrink-0 text-3xl">⚠️</div>
            <div class="ml-4 flex-grow">
                <h3 class="text-lg leading-6 font-medium text-yellow-800">
                    Activación Requerida
                </h3>
                <div class="mt-2 text-sm text-yellow-700">
                    <p>Tu ecosistema está en riesgo. Tienes <span id="timer" class="font-mono font-bold text-xl bg-yellow-200 px-2 rounded">Cargando...</span> para realizar el pago de suscripción.</p>
                </div>
                <div class="mt-4">
                    <a href="{{ wa_link }}" target="_blank" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 shadow-lg transition-all transform hover:scale-105">
                        📱 Pagar $50.000 y Activar Ahora
                    </a>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div class="bg-white p-6 rounded-xl shadow hover:shadow-lg transition-all border border-gray-100 group cursor-pointer">
            <div class="w-12 h-12 bg-black text-white rounded-full flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">✂️</div>
            <h3 class="text-xl font-bold font-serif mb-2">Mis Servicios</h3>
            <p class="text-gray-500 text-sm mb-4">Configura cortes, precios y tiempos de duración.</p>
            <span class="text-xs font-bold underline">Gestionar Servicios &rarr;</span>
        </div>

        <div class="bg-white p-6 rounded-xl shadow hover:shadow-lg transition-all border border-gray-100 group cursor-pointer">
            <div class="w-12 h-12 bg-gray-200 text-black rounded-full flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">👥</div>
            <h3 class="text-xl font-bold font-serif mb-2">Mi Equipo</h3>
            <p class="text-gray-500 text-sm mb-4">Crea usuarios para tus empleados y define turnos.</p>
            <span class="text-xs font-bold underline">Gestionar Empleados &rarr;</span>
        </div>

        <div class="bg-white p-6 rounded-xl shadow hover:shadow-lg transition-all border border-gray-100 group cursor-pointer">
            <div class="w-12 h-12 bg-gray-200 text-black rounded-full flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">📅</div>
            <h3 class="text-xl font-bold font-serif mb-2">Horarios & Cierre</h3>
            <p class="text-gray-500 text-sm mb-4">Define a qué hora abre y cierra tu local.</p>
            <span class="text-xs font-bold underline">Configurar Reloj &rarr;</span>
        </div>

    </div>

    <div class="mt-12">
        <h2 class="text-2xl font-serif font-bold mb-4">Agenda de Hoy</h2>
        <div class="bg-white rounded-xl shadow p-8 text-center border border-gray-100">
            <p class="text-gray-400">Aún no tienes citas agendadas para hoy.</p>
        </div>
    </div>

</div>

<script>
    // Recibimos los segundos restantes desde Django
    let timeLeft = {{ seconds_left }};
    
    function updateTimer() {
        if (timeLeft <= 0) {
            document.getElementById("timer").innerHTML = "00:00:00";
            document.getElementById("timer").classList.add("text-red-600");
            return;
        }

        let hours = Math.floor(timeLeft / 3600);
        let minutes = Math.floor((timeLeft % 3600) / 60);
        let seconds = timeLeft % 60;

        // Formato con ceros a la izquierda (09:05:01)
        let formattedTime = 
            (hours < 10 ? "0" + hours : hours) + ":" + 
            (minutes < 10 ? "0" + minutes : minutes) + ":" + 
            (seconds < 10 ? "0" + seconds : seconds);

        document.getElementById("timer").innerHTML = formattedTime;
        timeLeft--;
    }

    // Actualizar cada segundo
    setInterval(updateTimer, 1000);
    updateTimer(); // Ejecutar inmediatamente al cargar
</script>
{% endblock %}
"""

# ==========================================
# 4. EJECUTAR ACTUALIZACIÓN
# ==========================================
def run_upgrade():
    print("🚀 INICIANDO ACTUALIZACIÓN DEL DASHBOARD...")

    # 1. Base HTML (Navbar)
    with open(BASE_DIR / 'templates' / 'base.html', 'w', encoding='utf-8') as f:
        f.write(base_html_content.strip())
    print("✅ templates/base.html: Navbar y Footer integrados.")

    # 2. Views (Lógica Timer y WhatsApp)
    with open(BASE_DIR / 'apps' / 'businesses' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_dashboard_content.strip())
    print("✅ apps/businesses/views.py: Lógica de 'The Reaper' implementada.")

    # 3. Dashboard HTML (JS y Botones)
    with open(BASE_DIR / 'templates' / 'businesses' / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_dashboard_content.strip())
    print("✅ templates/businesses/dashboard.html: Interfaz renovada.")

if __name__ == "__main__":
    run_upgrade()
    print("\n✨ TODO LISTO.")
    print("1. Ejecuta: python manage.py runserver")
    print("2. Entra al Panel. Verás:")
    print("   - Barra de navegación con tu nombre.")
    print("   - Cronómetro regresivo real.")
    print("   - Botón verde que abre WhatsApp con tu ID.")