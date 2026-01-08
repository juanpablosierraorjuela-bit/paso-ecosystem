from django.shortcuts import render, redirect, get_object_or_404
from apps.businesses.models import Salon, Service, Booking
# Importamos la lógica de reserva que ya funciona en businesses
# para no duplicar código ni romper la base de datos.

def marketplace_home(request):
    # Buscador simple
    q = request.GET.get('q', '')
    city = request.GET.get('city', '')
    salons = Salon.objects.all()
    
    if q:
        salons = salons.filter(name__icontains=q)
    if city:
        salons = salons.filter(city=city)
        
    cities = Salon.objects.values_list('city', flat=True).distinct()
    return render(request, 'marketplace/index.html', {'salons': salons, 'cities': cities})

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    return render(request, 'marketplace/salon_detail.html', {'salon': salon})

def booking_create(request, service_id):
    # Redirige al wizard de businesses que ya está probado
    # Guardamos el servicio en sesión para iniciar el flujo
    request.session['booking_service'] = service_id
    service = get_object_or_404(Service, id=service_id)
    request.session['booking_salon'] = service.salon.id
    return redirect('booking_step_employee')

def booking_success(request, pk):
    return render(request, 'marketplace/booking_success.html')
