from datetime import datetime, timedelta, time
from .models import Booking

def get_available_slots(employee, service, date_obj):
    """
    Calcula disponibilidad real cruzando:
    1. Horario del empleado.
    2. Hora de almuerzo.
    3. Citas ya existentes.
    4. Duración del servicio + Buffer.
    5. Hora de cierre del negocio.
    """
    # 1. Obtener horario base del día
    day_name = date_obj.strftime('%A').lower()
    schedule_str = getattr(employee.schedule, f"{day_name}_hours", "CERRADO")
    
    if schedule_str == "CERRADO" or not schedule_str:
        return [] # No trabaja hoy

    try:
        start_s, end_s = schedule_str.split('-')
        work_start = datetime.strptime(start_s, "%H:%M").time()
        work_end = datetime.strptime(end_s, "%H:%M").time()
    except:
        return []

    # 2. Definir duración total del bloque necesario
    block_minutes = service.duration + service.buffer_time
    
    # 3. Obtener citas existentes (Bloqueos)
    bookings = Booking.objects.filter(
        employee=employee,
        date_time__date=date_obj
    ).exclude(status='CANCELLED')

    # 4. Generar slots
    available_slots = []
    current_time = datetime.combine(date_obj, work_start)
    limit_time = datetime.combine(date_obj, work_end)
    
    lunch_start = employee.schedule.lunch_start
    lunch_end = employee.schedule.lunch_end

    while current_time + timedelta(minutes=block_minutes) <= limit_time:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=block_minutes)
        is_viable = True
        
        # A. Validar Almuerzo
        if lunch_start and lunch_end:
            l_start = datetime.combine(date_obj, lunch_start)
            l_end = datetime.combine(date_obj, lunch_end)
            # Si la cita empieza antes del almuerzo y termina después del inicio del almuerzo = COLISIÓN
            if slot_start < l_end and slot_end > l_start:
                is_viable = False

        # B. Validar Citas Existentes
        if is_viable:
            for b in bookings:
                # Lógica de colisión de rangos
                if slot_start < b.end_time and slot_end > b.date_time:
                    is_viable = False
                    break
        
        if is_viable:
            available_slots.append(current_time.strftime("%H:%M"))
            
        current_time += timedelta(minutes=30) # Intervalos de 30 min

    return available_slots
