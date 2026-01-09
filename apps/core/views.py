from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import OwnerRegistrationForm

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente
            login(request, user)
            messages.success(request, '¡Bienvenido! Tu ecosistema ha sido creado. Tienes 24h para activarlo.')
            return redirect('dashboard') # Redirige al panel de dueño
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = OwnerRegistrationForm()
    
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    return render(request, 'registration/login.html')