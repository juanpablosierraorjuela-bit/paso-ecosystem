import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. NUEVA LANDING PAGE (COPYWRITING PERSUASIVO)
# ==========================================
html_landing = """
{% extends 'base.html' %}

{% block content %}
<div class="bg-white">
    <div class="relative bg-black text-white overflow-hidden">
        <div class="absolute inset-0 opacity-20">
            <img src="https://images.unsplash.com/photo-1585747860715-2ba37e788b70?q=80&w=2074&auto=format&fit=crop" class="w-full h-full object-cover" alt="Barberia">
        </div>
        <div class="relative container mx-auto px-4 py-24 md:py-32 text-center">
            <span class="bg-yellow-500 text-black text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide mb-4 inline-block">Para Dueños de Negocio</span>
            <h1 class="text-4xl md:text-6xl font-serif font-bold mb-6 leading-tight">
                ¿Tu agenda es de papel <br> pero tus clientes viven en el celular?
            </h1>
            <p class="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
                Deja de ser el recepcionista de tu propio negocio. Automatiza citas, asegura pagos y elimina las inasistencias con el Ecosistema PASO.
            </p>
            <a href="{% url 'register_owner' %}" class="bg-white text-black font-bold py-4 px-8 rounded-full hover:bg-gray-200 transition transform hover:scale-105 shadow-xl text-lg">
                🚀 Únete al Ecosistema
            </a>
            <p class="mt-4 text-sm text-gray-400">Prueba de 24 horas sin compromiso</p>
        </div>
    </div>

    <div class="py-20 bg-gray-50">
        <div class="container mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-serif font-bold text-gray-900">¿Te suena familiar esta rutina?</h2>
                <p class="text-gray-500 mt-2">Los 3 enemigos silenciosos de tu rentabilidad.</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
                <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition">
                    <div class="text-4xl mb-4">📒</div>
                    <h3 class="text-xl font-bold mb-3">"La Agenda de Papel"</h3>
                    <p class="text-gray-600 text-sm">
                        Borrones, tachones y citas dobles. Si no estás en el local, no sabes qué está pasando. Tu negocio depende de un cuaderno físico.
                    </p>
                </div>
                <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition">
                    <div class="text-4xl mb-4">💬</div>
                    <h3 class="text-xl font-bold mb-3">"El Chat Infinito"</h3>
                    <p class="text-gray-600 text-sm">
                        Responder 50 veces al día: <em>"¿Qué precio tiene?", "¿Tienes espacio a las 3?", "¿Quién me atiende?"</em>. Pierdes horas chateando en vez de facturando.
                    </p>
                </div>
                <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition">
                    <div class="text-4xl mb-4">👻</div>
                    <h3 class="text-xl font-bold mb-3">"El Cliente Fantasma"</h3>
                    <p class="text-gray-600 text-sm">
                        Te reservan, guardas el espacio, rechazas a otros... y nunca llegan. Perdiste dinero y tiempo de tu empleado.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <div class="py-20">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row items-center gap-12">
                <div class="w-full md:w-1/2">
                    <h2 class="text-3xl font-serif font-bold mb-6">No es una App, es tu Nuevo Sistema Operativo.</h2>
                    <div class="space-y-6">
                        <div class="flex">
                            <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-black text-white font-bold">1</div>
                            <div class="ml-4">
                                <h4 class="text-lg font-bold">Tu Recepcionista Virtual 24/7</h4>
                                <p class="text-gray-600 text-sm">Tus clientes ven tus servicios, precios y disponibilidad en tiempo real. Reservan solos, incluso mientras duermes.</p>
                            </div>
                        </div>
                        <div class="flex">
                            <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-black text-white font-bold">2</div>
                            <div class="ml-4">
                                <h4 class="text-lg font-bold">Adiós a las Inasistencias</h4>
                                <p class="text-gray-600 text-sm">El sistema exige un abono (que tú configuras) para confirmar. Tienen 60 minutos para pagar o el turno se libera. <span class="font-bold">Cero huecos vacíos.</span></p>
                            </div>
                        </div>
                        <div class="flex">
                            <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-black text-white font-bold">3</div>
                            <div class="ml-4">
                                <h4 class="text-lg font-bold">Gestión de Equipo y Turnos</h4>
                                <p class="text-gray-600 text-sm">Tus empleados gestionan su disponibilidad. Si el barbero almuerza a la 1 PM, el sistema no permite citas a esa hora. Sin errores humanos.</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="w-full md:w-1/2 bg-gray-100 rounded-3xl p-8 transform rotate-2 hover:rotate-0 transition duration-500 shadow-2xl">
                    <div class="bg-white rounded-xl shadow-lg p-6">
                        <div class="flex justify-between items-center mb-4 border-b pb-4">
                            <div class="font-bold text-lg">💈 Barber Shop El Patrón</div>
                            <div class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-bold">ABIERTO</div>
                        </div>
                        <div class="space-y-3">
                            <div class="h-8 bg-gray-100 rounded w-3/4"></div>
                            <div class="h-8 bg-gray-100 rounded w-1/2"></div>
                            <div class="mt-4 p-4 bg-yellow-50 border border-yellow-100 rounded-lg">
                                <p class="text-xs text-yellow-800 font-bold">Cita Pendiente de Pago</p>
                                <p class="text-xs text-gray-500">Corte Clásico • Juan • 4:00 PM</p>
                                <div class="mt-2 text-red-500 font-mono text-sm font-bold">59:30 restantes</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="bg-black text-white py-20 text-center">
        <div class="container mx-auto px-4">
            <h2 class="text-3xl font-serif font-bold mb-6">¿Listo para profesionalizar tu pasión?</h2>
            <p class="text-xl text-gray-400 mb-8">Únete a los negocios que ya no usan papel.</p>
            <div class="flex flex-col md:flex-row justify-center items-center gap-4">
                <a href="{% url 'register_owner' %}" class="bg-white text-black font-bold py-4 px-10 rounded-full hover:bg-gray-200 transition shadow-lg w-full md:w-auto">
                    Registrar Mi Negocio
                </a>
                <a href="{% url 'marketplace_home' %}" class="text-white border border-white font-bold py-4 px-10 rounded-full hover:bg-white hover:text-black transition w-full md:w-auto">
                    Ver Demo (Marketplace)
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 2. ACTUALIZAR VIEWS.PY (AGREGAR VISTA LANDING)
# ==========================================
core_views_content = """
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.businesses.forms import OwnerRegistrationForm
from apps.businesses.models import Salon
from apps.core.models import User, GlobalSettings
from apps.marketplace.models import Appointment
from apps.core.forms import ClientProfileForm, ClientPasswordForm
import re

def home(request):
    return render(request, 'home.html')

# --- NUEVA VISTA LANDING ---
def landing_owners(request):
    return render(request, 'landing_owners.html')

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    pass

@login_required
def dispatch_user(request):
    user = request.user
    if user.role == 'OWNER':
        return redirect('dashboard')
    elif user.role == 'CLIENT':
        return redirect('marketplace_home')
    elif user.role == 'EMPLOYEE':
        return redirect('employee_dashboard')
    elif user.is_superuser:
        return redirect('/admin/')
    else:
        return redirect('home')

@login_required
def client_dashboard(request):
    user = request.user
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ClientProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Tus datos han sido actualizados.")
                return redirect('client_dashboard')
        elif 'change_password' in request.POST:
            password_form = ClientPasswordForm(request.POST)
            if password_form.is_valid():
                new_pass = password_form.cleaned_data['new_password']
                user.set_password(new_pass)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect('client_dashboard')
    
    profile_form = ClientProfileForm(instance=user)
    password_form = ClientPasswordForm()
    
    appointments = Appointment.objects.filter(client=user).order_by('-created_at')
    
    for app in appointments:
        if app.status == 'PENDING':
            elapsed = timezone.now() - app.created_at
            remaining = timedelta(minutes=60) - elapsed
            app.seconds_left = max(0, int(remaining.total_seconds()))
            
            try:
                owner_phone = app.salon.owner.phone
                if owner_phone:
                    clean_phone = re.sub(r'\D', '', str(owner_phone))
                    if not clean_phone.startswith('57'):
                        clean_phone = '57' + clean_phone
                else:
                    clean_phone = '573000000000'
            except:
                clean_phone = '573000000000'
            
            msg = (
                f"Hola {app.salon.name}, soy {user.first_name}. "
                f"Confirmo mi cita para {app.service.name} el {app.date_time.strftime('%d/%m %I:%M %p')}. "
                f"Adjunto abono de ${int(app.deposit_amount)}."
            )
            app.wa_link = f"https://wa.me/{clean_phone}?text={msg}"
            
    context = {
        'appointments': appointments,
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'core/client_dashboard.html', context)
"""

# ==========================================
# 3. ACTUALIZAR URLS.PY (AGREGAR RUTA)
# ==========================================
core_urls_content = """
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    
    # NUEVA RUTA PARA LA LANDING
    path('soluciones-negocio/', views.landing_owners, name='landing_owners'),
    
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dispatch/', views.dispatch_user, name='dispatch'),
    path('mi-perfil/', views.client_dashboard, name='client_dashboard'),
]
"""

# ==========================================
# 4. ACTUALIZAR HOME.HTML (CAMBIAR LINK DEL BOTÓN)
# ==========================================
html_home = """
{% extends 'base.html' %}

{% block content %}
<div class="relative bg-white overflow-hidden">
    <div class="max-w-7xl mx-auto">
        <div class="relative z-10 pb-8 bg-white sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
            
            <main class="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
                <div class="sm:text-center lg:text-left">
                    <h1 class="text-4xl tracking-tight font-serif font-bold text-gray-900 sm:text-5xl md:text-6xl">
                        <span class="block xl:inline">El Ecosistema para</span>
                        <span class="block text-black xl:inline">tu belleza y estilo</span>
                    </h1>
                    <p class="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                        Descubre los mejores salones, barberías y spas de Colombia. Reserva en segundos, paga seguro y vive la experiencia PASO.
                    </p>
                    <div class="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                        <div class="rounded-md shadow">
                            <a href="{% url 'marketplace_home' %}" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-bold rounded-md text-white bg-black hover:bg-gray-800 md:py-4 md:text-lg md:px-10 transition-all">
                                🔍 Buscar Servicios
                            </a>
                        </div>
                        <div class="mt-3 sm:mt-0 sm:ml-3">
                            <a href="{% url 'landing_owners' %}" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-bold rounded-md text-black bg-yellow-100 hover:bg-yellow-200 md:py-4 md:text-lg md:px-10 transition-all">
                                💼 Soy Dueño
                            </a>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
    <div class="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
        <img class="h-56 w-full object-cover sm:h-72 md:h-96 lg:w-full lg:h-full" src="https://images.unsplash.com/photo-1560066984-138dadb4c035?ixlib=rb-1.2.1&auto=format&fit=crop&w=1934&q=80" alt="Salon de belleza lujoso">
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 5. ACTUALIZAR BASE.HTML (CAMBIAR LINK DEL NAVBAR)
# ==========================================
html_base = """
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
                <a href="{% url 'marketplace_home' %}" class="hover:text-yellow-400 transition">MARKETPLACE</a>
                
                {% if user.is_authenticated %}
                    <span class="text-gray-500 hidden md:inline">Hola, {{ user.first_name }}</span>
                    
                    {% if user.role == 'OWNER' %}
                        <a href="{% url 'dashboard' %}" class="bg-white text-black px-4 py-2 rounded-full hover:bg-gray-200 transition">
                            MI PANEL
                        </a>
                    {% elif user.role == 'CLIENT' %}
                        <a href="{% url 'client_dashboard' %}" class="bg-white text-black px-4 py-2 rounded-full hover:bg-gray-200 transition">
                            MIS CITAS
                        </a>
                    {% elif user.role == 'EMPLOYEE' %}
                        <a href="{% url 'employee_dashboard' %}" class="bg-white text-black px-4 py-2 rounded-full hover:bg-gray-200 transition">
                            MI AGENDA
                        </a>
                    {% endif %}
                    
                    <form action="{% url 'logout' %}" method="post" class="inline">
                        {% csrf_token %}
                        <button type="submit" class="text-red-400 hover:text-red-300 ml-2">SALIR</button>
                    </form>
                {% else %}
                    <a href="{% url 'landing_owners' %}" class="hidden md:inline hover:text-white text-gray-400">Soy Dueño</a>
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
            </div>
        </div>
    </footer>

</body>
</html>
"""

def execute_plan():
    print("🚀 CREANDO LANDING PAGE DE ALTA CONVERSIÓN...")

    # 1. Crear Template
    with open(BASE_DIR / 'templates' / 'landing_owners.html', 'w', encoding='utf-8') as f:
        f.write(html_landing.strip())
    print("✅ Landing creada: templates/landing_owners.html")

    # 2. Actualizar Views
    with open(BASE_DIR / 'apps' / 'core' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(core_views_content.strip())
    print("✅ Views actualizadas: Se agregó la vista landing_owners.")

    # 3. Actualizar URLs
    with open(BASE_DIR / 'apps' / 'core' / 'urls.py', 'w', encoding='utf-8') as f:
        f.write(core_urls_content.strip())
    print("✅ URLs actualizadas: Se agregó la ruta /soluciones-negocio/.")

    # 4. Actualizar Home
    with open(BASE_DIR / 'templates' / 'home.html', 'w', encoding='utf-8') as f:
        f.write(html_home.strip())
    print("✅ Home actualizado: Botón 'Soy Dueño' redireccionado.")

    # 5. Actualizar Base
    with open(BASE_DIR / 'templates' / 'base.html', 'w', encoding='utf-8') as f:
        f.write(html_base.strip())
    print("✅ NavBar actualizado: Enlace 'Soy Dueño' redireccionado.")

if __name__ == "__main__":
    execute_plan()