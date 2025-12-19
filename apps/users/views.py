from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages
from math import radians, cos, sin, asin, sqrt

from apps.businesses.models import Salon, Booking
# --- CORRECCIÓN: Usar SalonForm (el nombre correcto) ---
from apps.businesses.forms import SalonForm
from .forms import CustomUserCreationForm

# --- FUNCIÓN HAVERSINE ---
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 
    return c * r

# --- VISTA HOME ---
def home(request):
    salons = Salon.objects.all().order_by('-id')
    all_cities = Salon.objects.values_list('city', flat=True).distinct()

    if request.GET.get('city'):
        salons = salons.filter(city=request.GET.get('city'))

    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    nearby_search = False

    if lat and lon:
        nearby_search = True
        try:
            ulat, ulon = float(lat), float(lon)
            nearby = []
            for s in salons:
                if s.latitude and s.longitude:
                    try:
                        slat, slon = float(s.latitude), float(s.longitude)
                        dist = haversine(ulon, ulat, slon, slat)
                        if dist <= 0.6: # 600m
                            nearby.append(s)
                    except: continue
            salons = nearby
        except: pass

    return render(request, 'home.html', {
        'salons': salons,
        'all_cities': all_cities,
        'nearby_search': nearby_search
    })

# --- REGISTRO Y LOGIN ---
def register(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('role'): user.role = form.cleaned_data.get('role')
            user.save()
            login(request, user)
            
            if user.role == 'OWNER': return redirect('create_salon')
            elif user.role == 'EMPLOYEE': return redirect('employee_settings')
            else: return redirect('home')
    else: form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'OWNER':
        if hasattr(user, 'salon'): return render(request, 'dashboard/index.html', {'salon': user.salon})
        else: return redirect('create_salon')
    if user.role == 'EMPLOYEE': return redirect('employee_settings')
    bookings = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard/client_dashboard.html', {'bookings': bookings})

@login_required
def create_salon_view(request):
    if hasattr(request.user, 'salon'): return redirect('dashboard')
    if request.method == 'POST':
        # --- USAR SalonForm AQUÍ TAMBIÉN ---
        form = SalonForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                request.user.role = 'OWNER'
                request.user.save()
            messages.success(request, "¡Bienvenido! Configura tus servicios.")
            return redirect('dashboard') # Ajustado a dashboard
    else: form = SalonForm()
    return render(request, 'dashboard/create_salon.html', {'form': form})

def accept_invite_view(request): return redirect('dashboard')
def employee_join_view(request): return redirect('dashboard')