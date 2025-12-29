from datetime import datetime, timedelta, date, time
from django.utils import timezone
from .models import Booking, EmployeeSchedule

def get_available_slots(employee, check_date, service_duration):
    '''
    Genera lista de horas disponibles (ej: ['15:00', '15:30'])
    basado en el horario del empleado y citas existentes.
    '''
    # 1. Buscar horario del empleado para ese día de la semana
    weekday = check_date.weekday()
    try:
        schedule = EmployeeSchedule.objects.get(employee=employee, weekday=weekday, is_active=True)
    except EmployeeSchedule.DoesNotExist:
        return [] # El empleado no trabaja ese día

    # 2. Definir rango de trabajo (Ej: 3pm a 6pm)
    start_dt = datetime.combine(check_date, schedule.from_hour)
    end_dt = datetime.combine(check_date, schedule.to_hour)
    
    # Ajuste de zona horaria (simplificado para demo)
    # En producción usaríamos timezone.make_aware(start_dt)

    available_slots = []
    current_slot = start_dt

    # 3. Iterar cada 30 min (o duración del servicio)
    while current_slot + timedelta(minutes=service_duration) <= end_dt:
        slot_end = current_slot + timedelta(minutes=service_duration)
        
        # 4. Verificar si choca con una reserva existente
        collision = Booking.objects.filter(
            employee=employee,
            status='confirmed',
            start_time__lt=slot_end,
            end_time__gt=current_slot
        ).exists()

        if not collision:
            available_slots.append(current_slot.strftime("%H:%M"))

        current_slot += timedelta(minutes=30) # Saltos de 30 min

    return available_slots
