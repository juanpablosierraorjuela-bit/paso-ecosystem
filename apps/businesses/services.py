from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Booking, EmployeeSchedule

def check_availability(employee, start_time, duration_minutes):
    """
    Verifica si un empleado está libre:
    1. Dentro de su horario laboral.
    2. Fuera de su hora de almuerzo.
    3. Sin solapamiento con otras citas confirmadas.
    """
    end_time = start_time + timedelta(minutes=duration_minutes)
    weekday = start_time.weekday()
    current_time = start_time.time()
    current_end_time = end_time.time()

    # 1. Verificar Horario Laboral del Empleado
    try:
        schedule = employee.schedules.get(weekday=weekday)
    except EmployeeSchedule.DoesNotExist:
        return False, "El empleado no tiene horario configurado para este día."

    if schedule.is_closed:
        return False, "El empleado no trabaja hoy."

    if not (schedule.from_hour <= current_time and schedule.to_hour >= current_end_time):
        return False, "La hora seleccionada está fuera del turno laboral."

    # 2. Verificar Hora de Almuerzo
    # Si la cita empieza antes de terminar el almuerzo Y termina después de que empiece el almuerzo
    if employee.lunch_start and employee.lunch_end:
        if start_time.time() < employee.lunch_end and end_time.time() > employee.lunch_start:
             return False, "El horario choca con la hora de almuerzo."

    # 3. Verificar Solapamiento con otras citas (Atomicidad)
    # Buscamos citas que empiecen antes de que esta termine Y terminen después de que esta empiece
    conflicts = Booking.objects.filter(
        employee=employee,
        status='confirmed',
        start_time__lt=end_time, 
        end_time__gt=start_time
    ).exists()

    if conflicts:
        return False, "Ya existe una cita reservada en este horario."

    return True, "Disponible"

def create_booking_service(salon, service, customer, form_data):
    """
    Gestor transaccional para crear reservas.
    Maneja la lógica de 'Cualquier empleado' (Auto-assign).
    """
    start_time = form_data['start_time']
    employee = form_data.get('employee') # Puede ser None
    
    # Lógica de Asignación Automática
    selected_employee = None
    
    if employee:
        # El usuario eligió un empleado específico
        is_available, msg = check_availability(employee, start_time, service.duration_minutes)
        if not is_available:
            raise ValueError(f"{employee.name}: {msg}")
        selected_employee = employee
    else:
        # El usuario eligió "Cualquiera" -> Buscamos el primero disponible (Round Robin simple)
        candidates = salon.employees.all()
        for cand in candidates:
            is_available, _ = check_availability(cand, start_time, service.duration_minutes)
            if is_available:
                selected_employee = cand
                break
        
        if not selected_employee:
            raise ValueError("Lo sentimos, no hay estilistas disponibles a esta hora.")

    # Crear la Reserva de forma Atómica (Bloqueo de base de datos)
    with transaction.atomic():
        # Doble verificación final dentro de la transacción
        if Booking.objects.filter(
            employee=selected_employee,
            status='confirmed',
            start_time__lt=start_time + timedelta(minutes=service.duration_minutes),
            end_time__gt=start_time
        ).exists():
            raise ValueError("Alguien acaba de tomar este turno hace un segundo.")

        booking = Booking.objects.create(
            salon=salon,
            service=service,
            customer=customer if customer.is_authenticated else None,
            employee=selected_employee,
            customer_name=form_data['customer_name'],
            customer_phone=form_data['customer_phone'],
            start_time=start_time,
            end_time=start_time + timedelta(minutes=service.duration_minutes),
            status='confirmed'
        )
    
    return booking