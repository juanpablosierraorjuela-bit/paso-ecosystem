from datetime import datetime, timedelta, time
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        """
        Determina si el negocio está abierto en un momento específico,
        soportando horarios nocturnos (ej: Abre 10PM - Cierra 4AM).
        """
        if not check_time:
            check_time = timezone.localtime(timezone.now()).time()
        
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if open_t == close_t:
            return False # Nunca abre (o 24h? Asumimos cerrado si es igual por config simple)

        # Caso Normal: Abre 8am - Cierra 8pm
        if open_t < close_t:
            return open_t <= check_time <= close_t
        
        # Caso Nocturno/Amanecida: Abre 10pm - Cierra 4am
        else:
            # Es abierto si la hora actual es mayor a apertura (ej 11pm)
            # O si la hora actual es menor al cierre (ej 2am)
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, service, employee, target_date):
        """
        Genera los slots de tiempo disponibles para una fecha.
        Cruza: Horario Negocio + Duración Servicio + Citas Existentes.
        """
        # 1. Definir rango del día
        start_time = datetime.combine(target_date, salon.opening_time)
        
        # Manejo de cierre al día siguiente
        if salon.closing_time < salon.opening_time:
            end_time = datetime.combine(target_date + timedelta(days=1), salon.closing_time)
        else:
            end_time = datetime.combine(target_date, salon.closing_time)

        # 2. Generar bloques
        slots = []
        current = start_time
        service_duration = timedelta(minutes=service.duration_minutes + service.buffer_time)

        while current + service_duration <= end_time:
            # Aquí iría la lógica de verificar si 'current' choca con una cita existente
            # Por ahora (Fase 2 inicial), asumimos libre para mostrar la grilla
            
            slots.append({
                'time_obj': current,
                'label': current.strftime("%I:%M %p"),
                'is_available': True 
            })
            
            # Saltos de 30 min para opciones de agenda
            current += timedelta(minutes=30)
            
        return slots