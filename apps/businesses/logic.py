from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import Booking

def cleanup_expired_bookings():
    """
    Elimina citas pendientes con más de 50 minutos de antigüedad.
    Se ejecuta cada vez que alguien busca horarios (Lazy Cleanup).
    """
    limit_time = timezone.now() - timedelta(minutes=50)
    expired = Booking.objects.filter(status='PENDING_PAYMENT', created_at__lt=limit_time)
    expired.update(status='CANCELLED')

def get_available_slots(employee, service, date_obj):
    # 1. Limpieza automática antes de calcular
    cleanup_expired_bookings()

    salon = employee.salon
    day_name = date_obj.strftime('%A').lower()
    
    # Validar si el SALÓN abre ese día
    salon_works = getattr(salon, f"work_{day_name}", False)
    if not salon_works: return []

    # Validar horario del EMPLEADO
    schedule_str = getattr(employee.schedule, f"{day_name}_hours", "CERRADO")
    if schedule_str == "CERRADO": return []

    try:
        emp_start_s, emp_end_s = schedule_str.split('-')
        emp_start = datetime.strptime(emp_start_s, "%H:%M").time()
        emp_end = datetime.strptime(emp_end_s, "%H:%M").time()
    except: return []

    # REGLA DE ORO: El empleado no puede trabajar fuera del horario del Salón
    # Si el empleado entra a las 7am pero el salón abre a las 8am, el inicio es 8am.
    real_start = max(emp_start, salon.opening_time)
    real_end = min(emp_end, salon.closing_time)

    if real_start >= real_end: return []

    # Duración Total (Servicio + Buffer)
    block_minutes = service.duration + service.buffer_time
    
    # Citas existentes
    bookings = Booking.objects.filter(
        employee=employee,
        date_time__date=date_obj
    ).exclude(status='CANCELLED')

    available_slots = []
    current_time = datetime.combine(date_obj, real_start)
    limit_time = datetime.combine(date_obj, real_end)

    while current_time + timedelta(minutes=block_minutes) <= limit_time:
        slot_end = current_time + timedelta(minutes=block_minutes)
        is_viable = True
        
        # Verificar colisión con citas
        for b in bookings:
            # Si el hueco se cruza con una cita existente
            if current_time < b.end_time and slot_end > b.date_time:
                is_viable = False
                break
        
        if is_viable:
            available_slots.append(current_time.strftime("%H:%M"))
            
        current_time += timedelta(minutes=30)

    return available_slots
