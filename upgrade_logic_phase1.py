import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. EL ADMIN VITAMINEADO (SUPERUSUARIO)
# ==========================================
admin_content = """
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, GlobalSettings
import requests

# --- ACCIONES PERSONALIZADAS ---
@admin.action(description='✅ Verificar Pago (Activar Cuenta)')
def verify_payment(modeladmin, request, queryset):
    updated = queryset.update(is_verified_payment=True)
    modeladmin.message_user(request, f"{updated} dueños han sido marcados como PAGADOS.")

@admin.action(description='🚫 Revocar Pago (Desactivar)')
def revoke_payment(modeladmin, request, queryset):
    updated = queryset.update(is_verified_payment=False)
    modeladmin.message_user(request, f"{updated} dueños han sido marcados como PENDIENTES.")

# --- ADMIN DE USUARIOS ---
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'get_payment_status', 'city', 'date_joined')
    list_filter = ('role', 'is_verified_payment', 'city')
    actions = [verify_payment, revoke_payment]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Datos PASO', {'fields': ('role', 'phone', 'city', 'is_verified_payment', 'workplace')}),
    )

    # SEMÁFORO DE PAGOS
    def get_payment_status(self, obj):
        if obj.role == 'OWNER':
            if obj.is_verified_payment:
                return format_html('<span style="color:white; background:green; padding:3px 8px; border-radius:10px; font-weight:bold;">ACTIVO ($50k)</span>')
            else:
                return format_html('<span style="color:white; background:red; padding:3px 8px; border-radius:10px; font-weight:bold;">PENDIENTE</span>')
        return "-"
    get_payment_status.short_description = 'Estado de Suscripción'

# --- ADMIN DE CONFIGURACIÓN GLOBAL ---
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'whatsapp_support', 'telegram_status')
    
    def telegram_status(self, obj):
        if obj.telegram_token and obj.telegram_chat_id:
            return format_html('<span style="color:green;">✅ Conectado</span>')
        return format_html('<span style="color:gray;">⚪ Sin Configurar</span>')
    telegram_status.short_description = "Bot Telegram"

    # Botón para probar Telegram (Acción dummy para el ejemplo)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Aquí se podría disparar un mensaje de prueba
        
admin.site.register(User, CustomUserAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
"""

# ==========================================
# 2. SIGNALS (NOTIFICACIONES TELEGRAM)
# ==========================================
signals_content = """
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, GlobalSettings
import requests

def send_telegram_message(message):
    try:
        settings = GlobalSettings.objects.first()
        if settings and settings.telegram_token and settings.telegram_chat_id:
            url = f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage"
            data = {"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
            requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

@receiver(post_save, sender=User)
def notify_new_owner(sender, instance, created, **kwargs):
    if created and instance.role == 'OWNER':
        msg = (
            f"🚀 *NUEVO DUEÑO REGISTRADO*\\n\\n"
            f"👤 *Nombre:* {instance.first_name} {instance.last_name}\\n"
            f"🏪 *Usuario:* {instance.username}\\n"
            f"📍 *Ciudad:* {instance.city}\\n\\n"
            f"⚠️ *Estado:* Pendiente de Pago (24h restantes)"
        )
        send_telegram_message(msg)
"""

apps_core_content = """
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        import apps.core.signals
"""

# ==========================================
# 3. FORMS PARA DUEÑO (SERVICIOS/EMPLEADOS)
# ==========================================
forms_businesses_content = """
from django import forms
from .models import Service, Salon
from apps.core.models import User

# --- FORMULARIO DE SERVICIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']
        labels = {
            'name': 'Nombre del Servicio',
            'duration_minutes': 'Duración (minutos)',
            'price': 'Precio (COP)',
            'buffer_time': 'Tiempo de Limpieza (minutos)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO DE EMPLEADOS ---
class EmployeeCreationForm(forms.ModelForm):
    # Campos extra para crear el Usuario
    username = forms.CharField(label="Usuario de Acceso", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=True)
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO DE HORARIO (SALÓN) ---
class SalonScheduleForm(forms.ModelForm):
    opening_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora de Apertura")
    closing_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora de Cierre")

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'deposit_percentage']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
"""

# ==========================================
# 4. VISTAS DEL DUEÑO (LA LÓGICA CRUD)
# ==========================================
views_businesses_content = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings, User
from .models import Service, Salon
from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm

# --- DASHBOARD PRINCIPAL ---
@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        return redirect('home')
    
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner')

    # Lógica Timer
    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    # WhatsApp
    admin_settings = GlobalSettings.objects.first()
    admin_phone = admin_settings.whatsapp_support if admin_settings else '573000000000'
    wa_link = f"https://wa.me/{admin_phone}?text=Hola PASO, soy el negocio {salon.name} (ID {request.user.id}). Adjunto pago."

    # Métricas Rápidas
    service_count = salon.services.count()
    employee_count = salon.employees.count()

    context = {
        'salon': salon,
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment,
        'service_count': service_count,
        'employee_count': employee_count,
    }
    return render(request, 'businesses/dashboard.html', context)

# --- GESTIÓN DE SERVICIOS ---
@login_required
def services_list(request):
    salon = request.user.owned_salon
    services = salon.services.all()
    
    if request.method == 'POST':
        # Agregar Nuevo Servicio
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio creado exitosamente.")
            return redirect('services_list')
    else:
        form = ServiceForm()

    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('services_list')

# --- GESTIÓN DE EMPLEADOS ---
@login_required
def employees_list(request):
    salon = request.user.owned_salon
    employees = salon.employees.all()
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            # Crear Usuario
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                role='EMPLOYEE',
                workplace=salon,
                is_verified_payment=True # Empleados no pagan
            )
            messages.success(request, f"Empleado {user.first_name} creado.")
            return redirect('employees_list')
    else:
        form = EmployeeCreationForm()

    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk, workplace=request.user.owned_salon)
    employee.delete() # Ojo: Esto borra el usuario. Podrías solo quitarle el workplace.
    messages.success(request, "Empleado eliminado.")
    return redirect('employees_list')

# --- CONFIGURACIÓN DEL NEGOCIO (HORARIOS) ---
@login_required
def settings_view(request):
    salon = request.user.owned_salon
    if request.method == 'POST':
        form = SalonScheduleForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Horarios actualizados.")
            return redirect('settings_view')
    else:
        form = SalonScheduleForm(instance=salon)
    
    return render(request, 'businesses/settings.html', {'form': form, 'salon': salon})
"""

# ==========================================
# 5. TEMPLATES (SERVICIOS Y EMPLEADOS)
# ==========================================
html_services = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-serif font-bold">Mis Servicios</h1>
        <a href="{% url 'dashboard' %}" class="text-gray-500 hover:text-black">Volver al Panel</a>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="md:col-span-1 bg-white p-6 rounded-xl shadow border border-gray-100 h-fit">
            <h2 class="text-xl font-bold mb-4">Agregar Nuevo</h2>
            <form method="post">
                {% csrf_token %}
                {{ form.as_p }}
                <button type="submit" class="w-full mt-4 bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition">
                    Guardar Servicio
                </button>
            </form>
        </div>

        <div class="md:col-span-2 space-y-4">
            {% for service in services %}
            <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center group hover:border-black transition">
                <div>
                    <h3 class="text-lg font-bold">{{ service.name }}</h3>
                    <p class="text-sm text-gray-500">{{ service.duration_minutes }} min &bull; ${{ service.price }}</p>
                </div>
                <div>
                    <a href="{% url 'service_delete' service.pk %}" class="text-red-400 hover:text-red-600 text-sm font-bold border border-red-200 px-3 py-1 rounded hover:bg-red-50">
                        Eliminar
                    </a>
                </div>
            </div>
            {% empty %}
            <div class="text-center py-10 bg-gray-50 rounded-xl">
                <p class="text-gray-400">No tienes servicios creados aún.</p>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
"""

html_employees = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-serif font-bold">Mi Equipo</h1>
        <a href="{% url 'dashboard' %}" class="text-gray-500 hover:text-black">Volver al Panel</a>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="md:col-span-1 bg-white p-6 rounded-xl shadow border border-gray-100 h-fit">
            <h2 class="text-xl font-bold mb-4">Contratar Talento</h2>
            <form method="post">
                {% csrf_token %}
                {{ form.as_p }}
                <button type="submit" class="w-full mt-4 bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition">
                    Crear Empleado
                </button>
            </form>
        </div>

        <div class="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {% for employee in employees %}
            <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between group hover:border-black transition">
                <div class="flex items-center space-x-3 mb-4">
                    <div class="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center font-bold text-gray-600">
                        {{ employee.first_name|slice:":1" }}
                    </div>
                    <div>
                        <h3 class="text-lg font-bold">{{ employee.first_name }} {{ employee.last_name }}</h3>
                        <p class="text-xs text-gray-500">Usuario: {{ employee.username }}</p>
                    </div>
                </div>
                <div class="mt-auto">
                    <a href="{% url 'employee_delete' employee.pk %}" class="block text-center text-red-400 hover:text-red-600 text-sm font-bold border border-red-200 px-3 py-1 rounded hover:bg-red-50 w-full">
                        Desvincular
                    </a>
                </div>
            </div>
            {% empty %}
            <div class="col-span-2 text-center py-10 bg-gray-50 rounded-xl">
                <p class="text-gray-400">Aún no tienes empleados en tu equipo.</p>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
"""

html_settings = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow border border-gray-100">
        <div class="flex justify-between items-center mb-6 border-b pb-4">
            <h1 class="text-2xl font-serif font-bold">Configuración del Negocio</h1>
            <a href="{% url 'dashboard' %}" class="text-sm font-bold underline">Volver</a>
        </div>
        
        <form method="post" class="space-y-6">
            {% csrf_token %}
            
            <div class="grid grid-cols-2 gap-6">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Apertura</label>
                    {{ form.opening_time }}
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Cierre (Soporta Amanecida)</label>
                    {{ form.closing_time }}
                </div>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">% de Abono Requerido</label>
                {{ form.deposit_percentage }}
                <p class="text-xs text-gray-500 mt-1">El cliente deberá pagar esto para confirmar.</p>
            </div>

            <button type="submit" class="w-full bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition">
                Guardar Configuración
            </button>
        </form>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 6. ACTUALIZAR URLS.PY (BUSINESSES)
# ==========================================
urls_businesses_content = """
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    path('servicios/', views.services_list, name='services_list'),
    path('servicios/borrar/<int:pk>/', views.service_delete, name='service_delete'),
    path('equipo/', views.employees_list, name='employees_list'),
    path('equipo/borrar/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('configuracion/', views.settings_view, name='settings_view'),
]
"""

# ==========================================
# 7. EJECUTAR LOS CAMBIOS
# ==========================================
def apply_phase1():
    print("🧠 INYECTANDO LÓGICA DE NEGOCIO (FASE 1)...")

    # 1. Admin
    with open(BASE_DIR / 'apps' / 'core' / 'admin.py', 'w', encoding='utf-8') as f:
        f.write(admin_content.strip())
    print("✅ apps/core/admin.py: Panel Admin mejorado.")

    # 2. Signals
    with open(BASE_DIR / 'apps' / 'core' / 'signals.py', 'w', encoding='utf-8') as f:
        f.write(signals_content.strip())
    print("✅ apps/core/signals.py: Notificaciones Telegram listas.")

    # 3. Registrar Signals en apps.py
    with open(BASE_DIR / 'apps' / 'core' / 'apps.py', 'w', encoding='utf-8') as f:
        f.write(apps_core_content.strip())
    print("✅ apps/core/apps.py: Signals registrados.")

    # 4. Forms
    with open(BASE_DIR / 'apps' / 'businesses' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(forms_businesses_content.strip())
    print("✅ apps/businesses/forms.py: Formularios creados.")

    # 5. Views
    with open(BASE_DIR / 'apps' / 'businesses' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_businesses_content.strip())
    print("✅ apps/businesses/views.py: Lógica de Servicios y Empleados implementada.")

    # 6. URLs
    with open(BASE_DIR / 'apps' / 'businesses' / 'urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_businesses_content.strip())
    print("✅ apps/businesses/urls.py: Nuevas rutas activas.")

    # 7. Templates
    os.makedirs(BASE_DIR / 'templates' / 'businesses', exist_ok=True)
    
    with open(BASE_DIR / 'templates' / 'businesses' / 'services.html', 'w', encoding='utf-8') as f:
        f.write(html_services.strip())
    
    with open(BASE_DIR / 'templates' / 'businesses' / 'employees.html', 'w', encoding='utf-8') as f:
        f.write(html_employees.strip())

    with open(BASE_DIR / 'templates' / 'businesses' / 'settings.html', 'w', encoding='utf-8') as f:
        f.write(html_settings.strip())

    print("✅ Templates HTML creados.")

    # 8. Modificar el Dashboard para enlazar los botones
    # Necesitamos leer el dashboard actual y asegurarnos que los links apuntan a las nuevas URLs
    # Por simplicidad, sobrescribimos el Dashboard con la versión que tiene los links correctos
    dashboard_update = """
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

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-gray-900 text-white p-4 rounded-lg">
            <p class="text-xs text-gray-400">SERVICIOS ACTIVOS</p>
            <p class="text-2xl font-bold">{{ service_count }}</p>
        </div>
        <div class="bg-gray-900 text-white p-4 rounded-lg">
            <p class="text-xs text-gray-400">EMPLEADOS</p>
            <p class="text-2xl font-bold">{{ employee_count }}</p>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <a href="{% url 'services_list' %}" class="bg-white p-6 rounded-xl shadow hover:shadow-lg transition-all border border-gray-100 group cursor-pointer block">
            <div class="w-12 h-12 bg-black text-white rounded-full flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">✂️</div>
            <h3 class="text-xl font-bold font-serif mb-2">Mis Servicios</h3>
            <p class="text-gray-500 text-sm mb-4">Configura cortes, precios y tiempos de duración.</p>
            <span class="text-xs font-bold underline">Gestionar Servicios &rarr;</span>
        </a>

        <a href="{% url 'employees_list' %}" class="bg-white p-6 rounded-xl shadow hover:shadow-lg transition-all border border-gray-100 group cursor-pointer block">
            <div class="w-12 h-12 bg-gray-200 text-black rounded-full flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">👥</div>
            <h3 class="text-xl font-bold font-serif mb-2">Mi Equipo</h3>
            <p class="text-gray-500 text-sm mb-4">Crea usuarios para tus empleados y define turnos.</p>
            <span class="text-xs font-bold underline">Gestionar Empleados &rarr;</span>
        </a>

        <a href="{% url 'settings_view' %}" class="bg-white p-6 rounded-xl shadow hover:shadow-lg transition-all border border-gray-100 group cursor-pointer block">
            <div class="w-12 h-12 bg-gray-200 text-black rounded-full flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">📅</div>
            <h3 class="text-xl font-bold font-serif mb-2">Horarios & Cierre</h3>
            <p class="text-gray-500 text-sm mb-4">Define a qué hora abre y cierra tu local.</p>
            <span class="text-xs font-bold underline">Configurar Reloj &rarr;</span>
        </a>

    </div>

    <div class="mt-12">
        <h2 class="text-2xl font-serif font-bold mb-4">Agenda de Hoy</h2>
        <div class="bg-white rounded-xl shadow p-8 text-center border border-gray-100">
            <p class="text-gray-400">Aún no tienes citas agendadas para hoy.</p>
        </div>
    </div>

</div>

<script>
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

        let formattedTime = 
            (hours < 10 ? "0" + hours : hours) + ":" + 
            (minutes < 10 ? "0" + minutes : minutes) + ":" + 
            (seconds < 10 ? "0" + seconds : seconds);

        document.getElementById("timer").innerHTML = formattedTime;
        timeLeft--;
    }
    setInterval(updateTimer, 1000);
    updateTimer();
</script>
{% endblock %}
"""
    with open(BASE_DIR / 'templates' / 'businesses' / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_update.strip())
    print("✅ Dashboard actualizado con enlaces.")

if __name__ == "__main__":
    apply_phase1()
    print("\n✨ FASE 1 COMPLETADA. Ahora tienes:")
    print("1. Admin con colores y Telegram.")
    print("2. Panel de Servicios (Crear/Borrar).")
    print("3. Panel de Empleados (Contratar/Despedir).")
    print("4. Panel de Configuración (Horarios).")
    print("🚀 Siguiente paso: Sube a GitHub y prueba.")