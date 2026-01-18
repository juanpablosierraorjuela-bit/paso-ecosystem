from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from decimal import Decimal
from apps.businesses.models import Salon, Service
from apps.core.models import User
from apps.businesses.logic import AvailabilityManager
from apps.marketplace.models import Appointment
import uuid
import urllib.parse

def home(request):
    query = request.GET.get('q', '')
    city_filter = request.GET.get('city', '')
    salons = Salon.objects.select_related('owner').all()

    if query:
        salons = salons.filter(name__icontains=query)
    
    if city_filter:
        salons = salons.filter(city=city_filter)

    for salon in salons:
        salon.is_open_now = AvailabilityManager.is_salon_open(salon)
        
    city_list = Salon.objects.values_list('city', flat=True).distinct().order_by('city')

    context = {
        'salons': salons,
        'cities': city_list,
        'current_city': city_filter,
        'current_query': query
    }
    return render(request, 'marketplace/home.html', context)

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    services = salon.services.all()
    return render(request, 'marketplace/salon_detail.html', {'salon': salon, 'services': services})

@login_required
def booking_wizard(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    service_ids = request.GET.getlist('services')
    services = Service.objects.filter(id__in=service_ids, salon=salon)
    
    if not services:
        messages.error(request, "Debes seleccionar al menos un servicio.")
        return redirect('salon_detail', pk=salon_id)
    
    employees = salon.employees.all()
    
    context = {
        'salon': salon,
        'services': services,
        'employees': employees,
        'service_ids_str': ",".join(service_ids)
    }
    return render(request, 'marketplace/booking_wizard.html', context)

@require_GET
def get_available_slots_api(request):
    salon_id = request.GET.get('salon_id')
    employee_id = request.GET.get('employee_id')
    date_str = request.GET.get('date')
    service_ids = request.GET.get('services', '').split(',')

    if not all([salon_id, employee_id, date_str]):
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)

    salon = get_object_or_404(Salon, id=salon_id)
    employee = get_object_or_404(User, id=employee_id)
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    services_list = Service.objects.filter(id__in=service_ids)

    slots = AvailabilityManager.get_available_slots(salon, services_list, employee, target_date)
    return JsonResponse({'slots': slots})

@login_required
def booking_commit(request):
    """
    Crea la cita asegurando que el empleado seleccionado quede guardado.
    """
    if request.method == 'POST':
        try:
            salon_id = request.POST.get('salon_id')
            employee_id = request.POST.get('employee_id')
            service_ids = request.POST.get('service_ids').split(',')
            date_str = request.POST.get('selected_date')
            slot_str = request.POST.get('selected_slot')

            salon = get_object_or_404(Salon, id=salon_id)
            employee = get_object_or_404(User, id=employee_id)
            services = Service.objects.filter(id__in=service_ids)
            
            # Combinar fecha y hora
            naive_dt = datetime.strptime(f"{date_str} {slot_str}", '%Y-%m-%d %H:%M')
            dt = timezone.make_aware(naive_dt)

            total_price = sum(s.price for s in services)
            deposit = (total_price * salon.deposit_percentage) / 100

            # CORRECCIÓN: Se asigna explícitamente el empleado al crear la cita
            appointment = Appointment.objects.create(
                client=request.user,
                salon=salon,
                employee=employee,
                date_time=dt,
                status='PENDING',
                total_price=total_price,
                deposit_amount=deposit
            )
            appointment.services.set(services)
            
            messages.success(request, "¡Cita reservada! Tienes 60 minutos para realizar el abono.")
            return redirect('client_dashboard')

        except Exception as e:
            messages.error(request, f"Hubo un error al procesar tu reserva: {str(e)}")
            return redirect('marketplace_home')
            
    return redirect('marketplace_home')

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user == appointment.client or request.user.role == 'OWNER':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "La cita ha sido cancelada.")
    else:
        messages.error(request, "No tienes permiso para cancelar esta cita.")
    return redirect('client_dashboard')

@login_required
def client_dashboard(request):
    appointments = Appointment.objects.filter(client=request.user).prefetch_related('services', 'salon').order_by('-created_at')
    
    for app in appointments:
        if app.status == 'PENDING':
            expire_at = app.created_at + timedelta(minutes=60)
            app.expire_timestamp = int(expire_at.timestamp() * 1000)
            
            owner_phone = app.salon.owner.phone if app.salon.owner.phone else ""
            msg = f"Hola, soy {request.user.first_name}. Envío el comprobante de mi abono para la cita de {app.date_time.strftime('%d/%m %H:%M')}."
            app.wa_link = f"https://wa.me/{owner_phone}?text={urllib.parse.quote(msg)}"
            
    return render(request, 'marketplace/client_dashboard.html', {'appointments': appointments})