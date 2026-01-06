from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Salon, Appointment
from apps.businesses.models import Service, EmployeeSchedule
from django.utils import timezone
from datetime import datetime, timedelta

def marketplace_home(request):
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    
    salons = Salon.objects.all()
    
    if query:
        # Búsqueda Semántica básica (Nombre o Descripción)
        salons = salons.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    if city:
        salons = salons.filter(city=city)
        
    return render(request, 'marketplace/index.html', {'salons': salons, 'query': query})

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    services = salon.services.filter(is_active=True)
    return render(request, 'marketplace/salon_detail.html', {'salon': salon, 'services': services})

@login_required
def booking_create(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    salon = service.salon
    
    if request.method == 'POST':
        # Simplificación para MVP: El usuario elige fecha/hora manualmente
        # En versión 'Dios' aquí va la lógica de cruce de horarios
        date_str = request.POST.get('date') # YYYY-MM-DD
        time_str = request.POST.get('time') # HH:MM
        
        if date_str and time_str:
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            start_dt = timezone.make_aware(start_dt)
            end_dt = start_dt + timedelta(minutes=service.duration)
            
            # Crear la cita PENDIENTE
            appt = Appointment.objects.create(
                client=request.user,
                salon=salon,
                service=service,
                employee=salon.owner, # Por defecto al dueño si no elige empleado (MVP)
                date_time=start_dt,
                end_time=end_dt,
                total_price=service.price,
                deposit_amount=service.price * (salon.deposit_percentage / 100)
            )
            return redirect('marketplace:booking_success', pk=appt.id)
            
    return render(request, 'marketplace/booking_wizard.html', {'service': service})

@login_required
def booking_success(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, client=request.user)
    # Link de WhatsApp para enviar comprobante
    msg = f"Hola, reservé {appt.service.name} para el {appt.date_time.strftime('%d/%m %H:%M')}. Envío mi abono de ${appt.deposit_amount:,.0f}."
    wa_link = f"https://wa.me/{appt.salon.owner.phone}?text={msg}"
    
    return render(request, 'marketplace/booking_success.html', {'appt': appt, 'wa_link': wa_link})