from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import OwnerRegistrationForm # Se creará luego

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        # Aquí irá la lógica de registro y guardado de timestamp
        pass
    return render(request, 'registration/register_owner.html')

def login_view(request):
    return render(request, 'registration/login.html')