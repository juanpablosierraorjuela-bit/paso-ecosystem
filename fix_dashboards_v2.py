import os
import subprocess
import sys

# ==========================================
# 1. CORE: LA VISTA INTELIGENTE (DISPATCHER)
# ==========================================
core_views = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import OwnerRegistrationForm
from django.urls import reverse_lazy
from .models import User

# --- REGISTRO DE DUEÑOS ---
class OwnerRegisterView(CreateView):
    model = User
    form_class = OwnerRegistrationForm
    template_name = 'registration/register_owner.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.OWNER
        user.save()
        return super().form_valid(form)

# --- HOME ---
def home(request):
    return render(request, 'home.html')

# --- DISPATCHER: EL CEREBRO DE REDIRECCIÓN ---
@login_required
def dashboard_redirect(request):
    \"\"\"
    Esta función decide a dónde va el usuario según su rol
    después de iniciar sesión.
    \"\"\"
    user = request.user
    
    if user.role == User.Role.OWNER:
        return redirect('businesses:dashboard')
    elif user.role == User.Role.EMPLOYEE:
        return redirect('booking:employee_dashboard')
    elif user.role == User.Role.CLIENT:
        return redirect('booking:client_dashboard')
    elif user.is_staff or user.is_superuser:
        return redirect('/admin/')
    
    # Si no tiene rol definido, al home
    return redirect('home')
"""

core_urls = """from django.urls import path
from .views import home, OwnerRegisterView, dashboard_redirect

urlpatterns = [
    path('', home, name='home'),
    path('registro-negocio/', OwnerRegisterView.as_view(), name='register_owner'),
    path('dashboard/', dashboard_redirect, name='dashboard'),
]
"""

# ==========================================
# 2. BUSINESSES: PANEL DE DUEÑO
# ==========================================
businesses_views = """from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def owner_dashboard(request):
    return render(request, 'businesses/dashboard.html')
"""

businesses_urls = """from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('panel/', views.owner_dashboard, name='dashboard'),
]
"""

template_owner_dashboard = """{% extends 'base.html' %}

{% block content %}
<div style="padding: 100px 5%; color: white;">
    <h1 style="color: #d4af37;">Panel de Control (Dueño)</h1>
    <p>Bienvenido, {{ user.first_name }}. Aquí gestionarás tu imperio.</p>
    <hr style="border-color: #333;">
    
    <div style="display: flex; gap: 20px; margin-top: 30px; flex-wrap: wrap;">
        <div style="background: #222; padding: 20px; border-radius: 10px; flex: 1; min-width: 250px;">
            <h3>⏰ Temporizador de Pago</h3>
            <p style="color: #ff4d4d;">23h 59m restantes</p>
            <button class="btn btn-primary" style="margin-top:10px;">Pagar Mensualidad</button>
        </div>
        <div style="background: #222; padding: 20px; border-radius: 10px; flex: 1; min-width: 250px;">
            <h3>📅 Agenda de Hoy</h3>
            <p>0 Citas pendientes</p>
        </div>
        <div style="background: #222; padding: 20px; border-radius: 10px; flex: 1; min-width: 250px;">
            <h3>⚙️ Configuración</h3>
            <p>Servicios, Empleados, Horarios</p>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 3. BOOKING: PANELES DE EMPLEADO Y CLIENTE
# ==========================================
booking_views = """from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def employee_dashboard(request):
    return render(request, 'booking/employee_dashboard.html')

@login_required
def client_dashboard(request):
    return render(request, 'booking/client_dashboard.html')
"""

booking_urls = """from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('mis-citas/', views.client_dashboard, name='client_dashboard'),
]
"""

template_employee_dashboard = """{% extends 'base.html' %}
{% block content %}
<div style="padding: 100px 5%; color: white;">
    <h1>Panel de Empleado</h1>
    <p>Tus citas asignadas aparecerán aquí.</p>
</div>
{% endblock %}
"""

template_client_dashboard = """{% extends 'base.html' %}
{% block content %}
<div style="padding: 100px 5%; color: white;">
    <h1>Mis Citas (Cliente)</h1>
    <p>Historial y reservas activas.</p>
</div>
{% endblock %}
"""

# ==========================================
# 4. CONFIGURACIÓN GLOBAL (URLS)
# ==========================================
config_urls = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('negocio/', include('apps.businesses.urls')),
    path('reservas/', include('apps.booking.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

def update_settings_redirect():
    """Cambia LOGIN_REDIRECT_URL a 'dashboard' en settings.py (UTF-8 FORZADO)"""
    path = 'config/settings.py'
    print(f"🔧 Configurando redirección en {path}...")
    try:
        # AQUÍ ESTABA EL ERROR: Agregamos encoding='utf-8'
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        found = False
        for line in lines:
            if 'LOGIN_REDIRECT_URL' in line:
                new_lines.append("LOGIN_REDIRECT_URL = 'dashboard'  # Redirige al Dispatcher\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append("\nLOGIN_REDIRECT_URL = 'dashboard'  # Redirige al Dispatcher\n")
            if 'LOGOUT_REDIRECT_URL' not in "".join(lines):
                new_lines.append("LOGOUT_REDIRECT_URL = 'home'\n")
            
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
    except FileNotFoundError:
        print("⚠️ No se encontró settings.py")
    except Exception as e:
        print(f"❌ Error leyendo settings.py: {e}")

# ==========================================
# 🛠️ UTILIDADES
# ==========================================
def write_file(path, content):
    print(f"📝 Escribiendo: {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def run_command(command):
    print(f"🚀 Ejecutando: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    print("🚦 CONSTRUYENDO SISTEMA DE REDIRECCIÓN INTELIGENTE (VERSIÓN UTF-8) 🚦")
    
    # 1. Core (Dispatcher)
    write_file('apps/core/views.py', core_views)
    write_file('apps/core/urls.py', core_urls)
    
    # 2. Businesses (Owner)
    write_file('apps/businesses/views.py', businesses_views)
    write_file('apps/businesses/urls.py', businesses_urls)
    write_file('templates/businesses/dashboard.html', template_owner_dashboard)
    
    # 3. Booking (Employee/Client)
    write_file('apps/booking/views.py', booking_views)
    write_file('apps/booking/urls.py', booking_urls)
    write_file('templates/booking/employee_dashboard.html', template_employee_dashboard)
    write_file('templates/booking/client_dashboard.html', template_client_dashboard)
    
    # 4. Config
    write_file('config/urls.py', config_urls)
    update_settings_redirect()
    
    # 5. Deploy
    print("\n📦 Subiendo arquitectura de paneles a Render...")
    try:
        run_command("git add .")
        run_command('git commit -m "Feat: Paneles de Roles y Redireccion Login V2"')
        run_command("git push origin main")
        print("\n✅ ¡LISTO! Script completado sin errores de codificación.")
    except Exception as e:
        print(f"⚠️ Error Git: {e}")

    try:
        os.remove(sys.argv[0])
    except:
        pass

if __name__ == "__main__":
    main()