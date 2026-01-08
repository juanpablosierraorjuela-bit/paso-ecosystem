import os
import subprocess
import sys

def reparar_y_finalizar():
    print("🚑 REPARANDO VIEWS.PY Y FINALIZANDO GÉNESIS...")

    # 1. ARREGLAR APPS/CORE_SAAS/VIEWS.PY
    # Agregamos la vista 'client_dashboard' que falta.
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
    # Vista placeholder para evitar el error en urls.py
    return render(request, 'client_dashboard.html')
"""

    os.makedirs(os.path.dirname(views_path), exist_ok=True)
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(views_content)
    print("✅ views.py reparado (se agregó client_dashboard).")

    # 2. INTENTAR MIGRACIONES DE NUEVO
    print("\n✨ Reintentando crear migraciones...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'core_saas', 'businesses'], check=True)
        print("✅ ¡MIGRACIONES CREADAS CON ÉXITO!")
        
        # 3. MIGRAR LA BASE DE DATOS (Para verificar que todo esté sano)
        print("📥 Aplicando migraciones a la DB local...")
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ Base de datos local lista y operativa.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error crítico: {e}")
        return

    print("\n🚀 ¡SISTEMA RESUCITADO Y LISTO!")
    print("Ahora sí, ejecuta estos comandos para subir la versión final a Render:")
    print("---------------------------------------------------")
    print("git add .")
    print("git commit -m \"Genesis Complete: Fix views and regenerate migrations\"")
    print("git push origin main")
    print("---------------------------------------------------")

if __name__ == "__main__":
    reparar_y_finalizar()