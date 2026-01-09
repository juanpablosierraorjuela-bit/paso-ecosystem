from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
from apps.businesses.models import Salon, Service
from apps.core.models import User
from apps.businesses.logic import AvailabilityManager
from apps.marketplace.models import Appointment
from apps.businesses.forms import COLOMBIA_CITIES # Importamos la lista oficial
import uuid

def home(request):
    # Obtener parámetros de búsqueda
    query = request.GET.get('q', '')
    city_filter = request.GET.get('city', '')

    # QuerySet base optimizado
    salons = Salon.objects.select_related('owner').all()

    # Aplicar filtros
    if query:
        salons = salons.filter(name__icontains=query)
    
    if city_filter:
        salons = salons.filter(city=city_filter)

    # Calcular estado abierto/cerrado solo para los resultados
    for salon in salons:
        salon.is_open_now = AvailabilityManager.is_salon_open(salon)
        
    # Extraer solo los nombres de las ciudades para el template
    city_list = [c[0] for c in COLOMBIA_CITIES]

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

def booking_wizard(request, salon_id, service_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    service = get_object_or_404(Service, pk=service_id, salon=salon)
    employees = salon.employees.all()
    
    deposit_amount = int((service.price * salon.deposit_percentage) / 100)
    
    context = {
        'salon': salon,
        'service': service,
        'employees': employees,
        'deposit_amount': deposit_amount,
        'today': timezone.localtime(timezone.now()).strftime('%Y-%m-%d'),
        'is_guest': not request.user.is_authenticated
    }
    return render(request, 'marketplace/booking_wizard.html', context)

@require_GET
def get_available_slots_api(request):
    try:
        salon_id = request.GET.get('salon_id')
        service_id = request.GET.get('service_id')
        employee_id = request.GET.get('employee_id')
        date_str = request.GET.get('date')

        salon = get_object_or_404(Salon, pk=salon_id)
        service = get_object_or_404(Service, pk=service_id)
        employee = get_object_or_404(User, pk=employee_id)
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        slots = AvailabilityManager.get_available_slots(salon, service, employee, target_date)
        
        json_slots = []
        for slot in slots:
            json_slots.append({
                'time': slot['time_obj'].strftime('%H:%M'),
                'label': slot['label'],
                'available': slot['is_available']
            })
            
        return JsonResponse({'slots': json_slots})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def booking_commit(request):
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        service_id = request.POST.get('service_id')
        employee_id = request.POST.get('employee_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        salon = get_object_or_404(Salon, pk=salon_id)
        service = get_object_or_404(Service, pk=service_id)
        employee = get_object_or_404(User, pk=employee_id)
        
        booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        booking_datetime = timezone.make_aware(booking_datetime)
        deposit_val = (service.price * salon.deposit_percentage) / 100

        client_user = request.user

        if not client_user.is_authenticated:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Este correo ya está registrado. Por favor inicia sesión primero.")
                return redirect('login')
            
            temp_password = str(uuid.uuid4())[:8]
            
            client_user = User.objects.create_user(
                username=email,
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='CLIENT',
                is_verified_payment=True
            )
            
            login(request, client_user)
            messages.success(request, f"¡Cuenta creada! Tu contraseña temporal es: {temp_password}")

        Appointment.objects.create(
            client=client_user,
            salon=salon,
            service=service,
            employee=employee,
            date_time=booking_datetime,
            total_price=service.price,
            deposit_amount=deposit_val,
            status='PENDING'
        )
        
        return redirect('client_dashboard')
        
    return redirect('marketplace_home')