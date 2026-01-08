from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
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
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'registration/login.html')
