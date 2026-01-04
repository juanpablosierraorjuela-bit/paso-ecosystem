from datetime import datetime, timedelta, time
from .models import Booking, EmployeeSchedule

def get_available_slots(employee, service, date_obj):
    """
    Calcula los slots disponibles para un empleado en una fecha específica
    basándose en su horario y citas existentes.
    """
    # 1. Obtener horario del día (Ej: "09:00-18:00")
    day_name = date_obj.strftime('%A').lower() # monday, tuesday...
    schedule = getattr(employee.schedule, f"{day_name}_hours", "CERRADO")
    
    if schedule == "CERRADO" or not schedule:
        return []

    try:
        start_str, end_str = schedule.split('-')
        start_hour = datetime.strptime(start_str, "%H:%M").time()
        end_hour = datetime.strptime(end_str, "%H:%M").time()
    except ValueError:
        return []

    # 2. Definir duración total (Servicio + Buffer)
    total_duration = service.duration + service.buffer_time
    
    # 3. Obtener citas existentes ese día para ese empleado
    existing_bookings = Booking.objects.filter(
        employee=employee,
        date_time__date=date_obj,
        status__in=['PENDING_PAYMENT', 'IN_REVIEW', 'VERIFIED']
    )

    available_slots = []
    
    # 4. Iterar cada 30 min desde inicio a fin
    current_time = datetime.combine(date_obj, start_hour)
    end_datetime = datetime.combine(date_obj, end_hour)
    
    while current_time + timedelta(minutes=total_duration) <= end_datetime:
        slot_end = current_time + timedelta(minutes=total_duration)
        is_free = True
        
        # Verificar colisión con citas existentes
        for booking in existing_bookings:
            # Lógica de traslape: (InicioA < FinB) y (FinA > InicioB)
            if current_time < booking.end_time and slot_end > booking.date_time:
                is_free = False
                break
        
        if is_free:
            available_slots.append(current_time.strftime("%H:%M"))
            
        current_time += timedelta(minutes=30) # Saltos de 30 min
        
    return available_slots
