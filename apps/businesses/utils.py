from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta
from django.utils import timezone

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Retorna distancia en Kilómetros entre dos puntos usando Haversine.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 9999 
        
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 
    return c * r

def get_available_slots(employee, query_date, total_duration_minutes):
    """
    Retorna horas disponibles (HH:MM) validando horario del SALÓN y almuerzo del EMPLEADO.
    """
    from .models import Booking, OpeningHours  # Importación local para evitar ciclos

    # 1. Obtenemos el horario del SALÓN para ese día de la semana
    weekday = query_date.weekday() # 0=Lunes, 6=Domingo
    
    # Buscamos el horario de apertura de este salón específico
    schedule = OpeningHours.objects.filter(
        salon=employee.salon, 
        weekday=weekday, 
        is_closed=False
    ).first()
    
    if not schedule:
        return [] # El salón está cerrado o no tiene horario configurado ese día

    slots = []
    
    # Convertimos los horarios a datetime completos para poder sumar minutos
    current_time = datetime.combine(query_date, schedule.from_hour)
    end_time = datetime.combine(query_date, schedule.to_hour)
    
    # Horario de almuerzo del empleado
    lunch_start = None
    lunch_end = None
    if employee.lunch_start and employee.lunch_end:
        lunch_start = datetime.combine(query_date, employee.lunch_start)
        lunch_end = datetime.combine(query_date, employee.lunch_end)

    # 2. Buscamos citas existentes (BOOKING) del empleado
    day_start = datetime.combine(query_date, datetime.min.time())
    day_end = datetime.combine(query_date, datetime.max.time())
    
    # Usamos timezone aware si Django está configurado así, sino naive
    if timezone.is_aware(day_start):
        day_start = timezone.make_aware(day_start)
        day_end = timezone.make_aware(day_end)
    
    existing_bookings = Booking.objects.filter(
        employee=employee,
        start_time__range=(day_start, day_end)
    ).exclude(status='cancelled')

    step = timedelta(minutes=30) 
    duration_delta = timedelta(minutes=total_duration_minutes)

    # 3. Iteramos cada bloque de 30 min para ver si cabe la cita
    while current_time + duration_delta <= end_time:
        potential_start = current_time
        potential_end = current_time + duration_delta
        is_valid = True
        
        # A) Validar Almuerzo
        if lunch_start and lunch_end:
            # Si el servicio choca con la hora de almuerzo
            if potential_start < lunch_end and potential_end > lunch_start:
                is_valid = False

        # B) Validar Citas Existentes
        if is_valid:
            for booking in existing_bookings:
                # Convertimos booking times a naive para comparar si es necesario
                b_start = timezone.make_naive(booking.start_time) if timezone.is_aware(booking.start_time) else booking.start_time
                b_end = timezone.make_naive(booking.end_time) if timezone.is_aware(booking.end_time) else booking.end_time
                
                # Lógica de colisión
                if potential_start < b_end and potential_end > b_start:
                    is_valid = False
                    break
        
        if is_valid:
            slots.append(potential_start.time().strftime("%H:%M"))
        
        current_time += step

    return slots