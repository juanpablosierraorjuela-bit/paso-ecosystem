from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta, datetime, date

from .models import Booking, EmployeeSchedule, OpeningHours

def get_day_slots(salon, employee, target_date, service_duration=30):
    """
    Genera una lista de horarios disponibles para un día específico.
    Retorna una lista de diccionarios: [{'time': '09:00', 'value': '09:00'}, ...]
    """
    weekday = target_date.weekday()
    
    # 1. Determinar horario base (Del empleado o del salón)
    start_hour = None
    end_hour = None
    is_closed = False

    # Intentamos usar horario del empleado
    if employee:
        try:
            schedule = employee.schedules.get(weekday=weekday)
            if schedule.is_closed:
                return []
            start_hour = schedule.from_hour
            end_hour = schedule.to_hour
        except EmployeeSchedule.DoesNotExist:
            pass # Si no tiene horario propio, usamos el del salón

    # Si no hubo horario de empleado, usamos el del salón
    if not start_hour:
        try:
            schedule = salon.opening_hours.get(weekday=weekday)
            if schedule.is_closed:
                return []
            start_hour = schedule.from_hour
            end_hour = schedule.to_hour
        except OpeningHours.DoesNotExist:
            return [] # Cerrado por defecto

    # 2. Generar todos los slots de 30 mins (o duración del servicio)
    slots = []
    current_time = datetime.combine(target_date, start_hour)
    closing_time = datetime.combine(target_date, end_hour)
    
    # Ajuste: Si es HOY, no mostrar horas pasadas
    now = timezone.localtime(timezone.now())
    if target_date == now.date():
        if current_time < now.replace(tzinfo=None):
            # Avanzar current_time al próximo slot válido después de ahora
            # Redondear a la siguiente media hora
            minutes = now.minute
            add_minutes = 30 - (minutes % 30) if minutes % 30 != 0 else 0
            current_time = (now + timedelta(minutes=add_minutes)).replace(second=0, microsecond=0, tzinfo=None)

    while current_time + timedelta(minutes=service_duration) <= closing_time:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=service_duration)
        
        # 3. Verificar colisiones con reservas existentes
        # Buscamos si hay alguna reserva que se solape con este slot
        is_taken = Booking.objects.filter(
            salon=salon,
            employee=employee,
            status='confirmed',
            start_time__lt=timezone.make_aware(slot_end),
            end_time__gt=timezone.make_aware(slot_start)
        ).exists()

        # 4. Verificar almuerzo (si aplica)
        is_lunch = False
        if employee and employee.lunch_start and employee.lunch_end:
            l_start = datetime.combine(target_date, employee.lunch_start)
            l_end = datetime.combine(target_date, employee.lunch_end)
            if slot_start < l_end and slot_end > l_start:
                is_lunch = True

        if not is_taken and not is_lunch:
            slots.append({
                'label': slot_start.strftime('%I:%M %p'), # Formato 02:00 PM
                'value': slot_start.strftime('%H:%M')     # Formato 14:00
            })
        
        current_time += timedelta(minutes=30) # Saltos de 30 min fijos para grilla

    return slots

def create_booking_service(salon, service, customer, form_data):
    """
    Crea la reserva usando los datos validados.
    """
    start_time = form_data['start_time'] # Ya viene como datetime
    employee = form_data.get('employee')
    
    # Validación final de disponibilidad (doble check)
    is_taken = Booking.objects.filter(
        salon=salon,
        employee=employee,
        status='confirmed',
        start_time__lt=start_time + timedelta(minutes=service.duration_minutes),
        end_time__gt=start_time
    ).exists()

    if is_taken:
        raise ValueError("¡Lo sentimos! Alguien acaba de reservar este horario.")

    with transaction.atomic():
        booking = Booking.objects.create(
            salon=salon,
            service=service,
            customer=customer if customer and customer.is_authenticated else None,
            employee=employee,
            customer_name=form_data['customer_name'],
            customer_phone=form_data['customer_phone'],
            start_time=start_time,
            end_time=start_time + timedelta(minutes=service.duration_minutes),
            status='confirmed'
        )
    
    return booking