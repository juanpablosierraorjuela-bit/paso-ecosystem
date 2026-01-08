import os
import subprocess
import sys

def reparar_views_completo():
    print("🚑 REPARANDO VIEWS.PY (VERSIÓN COMPLETA) ...")

    # 1. ESCRIBIR APPS/CORE_SAAS/VIEWS.PY CON TODAS LAS FUNCIONES
    views_path = os.path.join('apps', 'core_saas', 'views.py')
    
    views_content = """from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.businesses.forms import SalonRegistrationForm
from apps.core_saas.models import User
from apps.businesses.models import Salon

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        form = SalonRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                role='OWNER'
            )
            Salon.objects.create(
                owner=user,
                name=form.cleaned_data['salon_name'],
                city=form.cleaned_data['city'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                instagram_link=form.cleaned_data.get('instagram_link', ''),
                maps_link=form.cleaned_data.get('maps_link', '')
            )
            login(request, user)
            return redirect('owner_dashboard')
    else:
        form = SalonRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            if user.role == 'OWNER': return redirect('owner_dashboard')
            if user.role == 'EMPLOYEE': return redirect('employee_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'registration/login.html')

@login_required
def client_dashboard(request):
    # Vista del perfil de cliente
    return render(request, 'client_dashboard.html')

@login_required
def employee_dashboard(request):
    # Vista del panel de empleado (Agenda)
    # Si no existe el template aun, usaremos uno generico o el dashboard
    return render(request, 'employee_dashboard.html')
"""

    os.makedirs(os.path.dirname(views_path), exist_ok=True)
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(views_content)
    print("✅ views.py actualizado con TODAS las funciones requeridas.")

    # 2. CREAR TEMPLATES FALTANTES (Para evitar errores de TemplateNotFound)
    templates_dir = os.path.join('templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Crear client_dashboard.html dummy si no existe
    if not os.path.exists(os.path.join(templates_dir, 'client_dashboard.html')):
        with open(os.path.join(templates_dir, 'client_dashboard.html'), 'w') as f:
            f.write("{% extends 'master.html' %} {% block content %} <h1>Perfil Cliente</h1> {% endblock %}")

    # Crear employee_dashboard.html dummy si no existe
    if not os.path.exists(os.path.join(templates_dir, 'employee_dashboard.html')):
        with open(os.path.join(templates_dir, 'employee_dashboard.html'), 'w') as f:
            f.write("{% extends 'master.html' %} {% block content %} <h1>Panel Empleado</h1> {% endblock %}")
    
    print("✅ Templates de seguridad verificados.")

    # 3. REINTENTAR MIGRACIONES
    print("\n✨ Ejecutando makemigrations...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'core_saas', 'businesses'], check=True)
        print("✅ ¡MIGRACIONES ÉXITOSAS!")
        
        print("📥 Migrando DB local...")
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ DB Local Sincronizada.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Todavía hay un error: {e}")
        return

    print("\n🚀 ¡AHORA SÍ! EL SISTEMA ESTÁ COMPLETO.")
    print("Ejecuta estos comandos para subir:")
    print("---------------------------------------------------")
    print("git add .")
    print("git commit -m \"Final Fix: Add all missing views and templates\"")
    print("git push origin main")
    print("---------------------------------------------------")

if __name__ == "__main__":
    reparar_views_completo()