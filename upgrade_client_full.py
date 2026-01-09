import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. CREAR FORMS.PY EN CORE (PERFIL CLIENTE)
# ==========================================
core_forms = """
from django import forms
from apps.core.models import User

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'phone': 'WhatsApp'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class ClientPasswordForm(forms.Form):
    new_password = forms.CharField(label="Nueva Contraseña", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
"""

# ==========================================
# 2. ACTUALIZAR VISTA CLIENT DASHBOARD
# ==========================================
core_views = """
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

# --- PANEL CLIENTE COMPLETO ---
@login_required
def client_dashboard(request):
    user = request.user
    
    # 1. Procesar Formularios si es POST
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
                update_session_auth_hash(request, user) # Mantener sesión activa
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect('client_dashboard')
    
    # 2. Cargar datos para la vista
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
# 3. NUEVO TEMPLATE (DOS COLUMNAS)
# ==========================================
html_dashboard = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8 border-b pb-4">
        <div>
            <h1 class="text-3xl font-serif font-bold text-gray-900">Hola, {{ user.first_name }}</h1>
            <p class="text-gray-500">Bienvenido a tu espacio personal.</p>
        </div>
        <div class="text-right">
            <span class="bg-gray-100 text-gray-600 text-xs font-bold px-3 py-1 rounded-full">
                CLIENTE
            </span>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="lg:col-span-2 space-y-6">
            <h2 class="text-xl font-bold flex items-center">
                📅 Mis Citas
            </h2>
            
            {% for app in appointments %}
            <div class="bg-white rounded-xl shadow border-l-4 {% if app.status == 'PENDING' %}border-yellow-400{% else %}border-green-500{% endif %} p-6 flex flex-col md:flex-row justify-between items-start md:items-center">
                
                <div class="mb-4 md:mb-0">
                    <div class="flex items-center space-x-2 mb-1">
                        <h3 class="text-xl font-bold">{{ app.service.name }}</h3>
                        {% if app.status == 'PENDING' %}
                            <span class="bg-yellow-100 text-yellow-800 text-xs font-bold px-2 py-0.5 rounded">PENDIENTE PAGO</span>
                        {% else %}
                            <span class="bg-green-100 text-green-800 text-xs font-bold px-2 py-0.5 rounded">CONFIRMADA</span>
                        {% endif %}
                    </div>
                    <p class="text-gray-600">{{ app.salon.name }} &bull; con {{ app.employee.first_name }}</p>
                    <p class="text-sm font-mono mt-1 text-gray-500">📅 {{ app.date_time|date:"D d M, Y - h:i A" }}</p>
                </div>

                <div class="w-full md:w-auto text-right">
                    {% if app.status == 'PENDING' %}
                        <p class="text-xs text-red-500 font-bold mb-2">
                            Tiempo para pagar: <span id="timer-{{ app.id }}">--:--</span>
                        </p>
                        <a href="{{ app.wa_link }}" target="_blank" class="block w-full md:inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-700 transition shadow-lg flex items-center justify-center">
                            <span class="mr-2">📱</span> Enviar Abono (${{ app.deposit_amount }})
                        </a>
                        
                        <script>
                            (function() {
                                let seconds = {{ app.seconds_left }};
                                const timerEl = document.getElementById('timer-{{ app.id }}');
                                const interval = setInterval(() => {
                                    if (seconds <= 0) {
                                        clearInterval(interval);
                                        timerEl.innerText = "EXPIRADO";
                                        return;
                                    }
                                    let m = Math.floor(seconds / 60);
                                    let s = seconds % 60;
                                    timerEl.innerText = `${m}:${s < 10 ? '0'+s : s}`;
                                    seconds--;
                                }, 1000);
                            })();
                        </script>
                    {% else %}
                        <button class="text-gray-400 text-sm border border-gray-200 px-4 py-2 rounded cursor-not-allowed bg-gray-50">
                            ✅ Comprobante Enviado
                        </button>
                    {% endif %}
                </div>
            </div>
            {% empty %}
            <div class="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
                <div class="text-4xl mb-2">📭</div>
                <p class="text-gray-500">No tienes citas agendadas.</p>
                <a href="{% url 'marketplace_home' %}" class="mt-4 inline-block text-black underline font-bold hover:text-gray-600">Ir al Marketplace</a>
            </div>
            {% endfor %}
        </div>

        <div class="lg:col-span-1 space-y-8">
            
            <div class="bg-white p-6 rounded-xl shadow border border-gray-100">
                <h3 class="text-lg font-bold mb-4">👤 Mis Datos</h3>
                <form method="post">
                    {% csrf_token %}
                    <div class="space-y-3">
                        {{ profile_form.as_p }}
                    </div>
                    <button type="submit" name="update_profile" class="mt-4 w-full bg-black text-white py-2 rounded-lg font-bold hover:bg-gray-800 transition text-sm">
                        Guardar Cambios
                    </button>
                </form>
            </div>

            <div class="bg-white p-6 rounded-xl shadow border border-gray-100">
                <h3 class="text-lg font-bold mb-4">🔒 Seguridad</h3>
                <form method="post">
                    {% csrf_token %}
                    <div class="space-y-3">
                        {{ password_form.as_p }}
                    </div>
                    <button type="submit" name="change_password" class="mt-4 w-full bg-white border border-gray-300 text-gray-700 py-2 rounded-lg font-bold hover:bg-gray-50 transition text-sm">
                        Actualizar Contraseña
                    </button>
                </form>
            </div>

        </div>
    </div>
</div>
{% endblock %}
"""

def apply_client_upgrade():
    print("🚀 MEJORANDO PANEL DEL CLIENTE (PERFIL + PASSWORD)...")

    # 1. Forms
    with open(BASE_DIR / 'apps' / 'core' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(core_forms.strip())
    print("✅ apps/core/forms.py: Formularios de cliente creados.")

    # 2. Views
    with open(BASE_DIR / 'apps' / 'core' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(core_views.strip())
    print("✅ apps/core/views.py: Lógica de actualización implementada.")

    # 3. Template
    with open(BASE_DIR / 'templates' / 'core' / 'client_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_dashboard.strip())
    print("✅ templates/core/client_dashboard.html: Interfaz renovada.")

if __name__ == "__main__":
    apply_client_upgrade()