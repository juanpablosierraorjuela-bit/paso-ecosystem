from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import urllib.parse

# Importes de tus modelos y lógica
from apps.businesses.models import Salon, Service
from apps.core.models import User
# Asegúrate de que logic.py esté en apps/businesses/logic.py
from apps.businesses.logic import AvailabilityManager
from apps.marketplace.models import Appointment

# --- VISTAS PÚBLICAS (MARKETPLACE) ---

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
    return render(request, 'marketplace/index.html', context)

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    is_open = AvailabilityManager.is_salon_open(salon)
    services = salon.services.all()
    return render(request, 'marketplace/salon_detail.html', {
        'salon': salon, 'is_open': is_open, 'services': services
    })

def booking_wizard(request, salon_id):
    """
    Paso 1 del agendamiento: Selección de Profesional y Fecha.
    """
    service_ids_str = request.GET.get('services', '')
    if not service_ids_str:
        messages.error(request, "Debes seleccionar al menos un servicio.")
        return redirect('salon_detail', pk=salon_id)
    
    # Validar IDs y evitar errores si hay comas vacías
    service_ids = [s for s in service_ids_str.split(',') if s.isdigit()]
    
    salon = get_object_or_404(Salon, pk=salon_id)
    services = Service.objects.filter(id__in=service_ids, salon=salon)
    
    # Filtramos usuarios que trabajen en este salón
    employees = User.objects.filter(workplace=salon)
    
    total_price = sum(s.price for s in services)
    deposit_perc = salon.deposit_percentage if salon.deposit_percentage else 0
    deposit_amount = int((total_price * deposit_perc) / 100)
    
    context = {
        'salon': salon,
        'services': services,
        'service_ids_str': service_ids_str,
        'employees': employees,
        'total_price': total_price,
        'deposit_amount': deposit_amount,
        'today': timezone.localtime(timezone.now()).date().isoformat(),
        'is_guest': not request.user.is_authenticated
    }
    return render(request, 'marketplace/booking_wizard.html', context)

@require_GET
def get_available_slots_api(request):
    """
    API crítica: Conecta el front con logic.py para ver disponibilidad real.
    """
    try:
        salon_id = request.GET.get('salon_id')
        service_ids = request.GET.get('service_ids', '').split(',')
        employee_id = request.GET.get('employee_id')
        date_str = request.GET.get('date')

        if not all([salon_id, employee_id, date_str]):
            return JsonResponse({'error': 'Faltan parámetros'}, status=400)

        salon = get_object_or_404(Salon, pk=salon_id)
        valid_service_ids = [s for s in service_ids if s and s.isdigit()]
        services = Service.objects.filter(id__in=valid_service_ids)
        employee = get_object_or_404(User, pk=employee_id)
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Llamamos a logic.py que ahora sí revisa el horario semanal
        slots = AvailabilityManager.get_available_slots(salon, list(services), employee, target_date)
        
        # logic.py ya devuelve los diccionarios formateados, los pasamos directo
        return JsonResponse({'slots': slots})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def booking_commit(request):
    """
    Guarda la reserva en la base de datos.
    """
    if request.method == 'POST':
        try:
            salon_id = request.POST.get('salon_id')
            service_ids = request.POST.get('service_ids', '').split(',')
            employee_id = request.POST.get('employee_id')
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            
            # Datos de contacto
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')

            salon = get_object_or_404(Salon, pk=salon_id)
            valid_service_ids = [s for s in service_ids if s and s.isdigit()]
            services = Service.objects.filter(id__in=valid_service_ids)
            employee = get_object_or_404(User, pk=employee_id)
            
            booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            booking_datetime = timezone.make_aware(booking_datetime)
            
            total_price = sum(s.price for s in services)
            deposit_perc = salon.deposit_percentage if salon.deposit_percentage else 0
            deposit_val = (Decimal(str(total_price)) * Decimal(str(deposit_perc))) / Decimal('100')

            client_user = request.user

            if not client_user.is_authenticated:
                if not email:
                    raise ValueError("El email es obligatorio para la reserva.")
                    
                user_exists = User.objects.filter(email=email).first()
                if user_exists:
                    client_user = user_exists
                    login(request, client_user)
                else:
                    temp_password = str(uuid.uuid4())[:8]
                    client_user = User.objects.create_user(
                        username=email, 
                        email=email, 
                        password=temp_password,
                        first_name=first_name or "Cliente", 
                        last_name=last_name or "Invitado", 
                        phone=phone,
                        role='CLIENT'
                    )
                    login(request, client_user)
                    messages.success(request, f"¡Cuenta creada! Tu clave temporal es: {temp_password}")

            appointment = Appointment.objects.create(
                client=client_user,
                salon=salon,
                employee=employee,
                date_time=booking_datetime,
                total_price=total_price,
                deposit_amount=deposit_val,
                status='PENDING'
            )
            appointment.services.set(services)
            
            messages.success(request, "Cita agendada correctamente.")
            return redirect('client_dashboard')
            
        except Exception as e:
            messages.error(request, f"Error en la reserva: {str(e)}")
            return redirect('marketplace_home')
            
    return redirect('marketplace_home')

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.user == appointment.client or request.user.role == 'OWNER':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "Cita cancelada correctamente.")
        
        if request.user.role == 'OWNER':
            return redirect('dashboard')
        return redirect('client_dashboard')
    
    messages.error(request, "No tienes permisos para cancelar esta cita.")
    return redirect('marketplace_home')

@login_required
def client_dashboard(request):
    appointments = Appointment.objects.filter(client=request.user).prefetch_related('services', 'salon').order_by('-created_at')
    
    for app in appointments:
        if app.status == 'PENDING':
            expire_at = app.created_at + timedelta(minutes=60)
            app.expire_timestamp = int(expire_at.timestamp() * 1000)
            
            owner_phone = app.salon.owner.phone if app.salon.owner and app.salon.owner.phone else ""
            msg = f"Hola, soy {request.user.first_name}. Envío el comprobante para mi cita del {app.date_time.strftime('%d/%m %H:%M')}."
            app.wa_link = f"https://wa.me/{owner_phone}?text={urllib.parse.quote(msg)}"
        else:
            app.expire_timestamp = 0
            app.wa_link = "#"

    return render(request, 'marketplace/client_dashboard.html', {
        'appointments': appointments,
    })