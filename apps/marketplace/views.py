from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from apps.businesses.models import Salon, Service
from apps.core.models import User
from apps.businesses.logic import AvailabilityManager

def home(request):
    # Traemos TODOS los salones con sus dueños
    salons = Salon.objects.select_related('owner').all()
    
    # Inyectamos el estado "Abierto/Cerrado" en tiempo real
    for salon in salons:
        salon.is_open_now = AvailabilityManager.is_salon_open(salon)
    
    return render(request, 'marketplace/index.html', {'salons': salons})

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    is_open = AvailabilityManager.is_salon_open(salon)
    services = salon.services.all()
    
    return render(request, 'marketplace/salon_detail.html', {
        'salon': salon,
        'is_open': is_open,
        'services': services
    })

def booking_wizard(request, salon_id, service_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    service = get_object_or_404(Service, pk=service_id, salon=salon)
    
    # Filtramos empleados que trabajan en este salón
    # (En el futuro filtraremos por especialidad si agregas eso)
    employees = salon.employees.all()
    
    # Fecha por defecto: Hoy
    target_date = timezone.localtime(timezone.now()).date()
    
    context = {
        'salon': salon,
        'service': service,
        'employees': employees,
        'target_date': target_date
    }
    return render(request, 'marketplace/booking_wizard.html', context)