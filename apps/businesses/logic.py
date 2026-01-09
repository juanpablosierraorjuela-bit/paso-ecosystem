from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        if not check_time:
            check_time = timezone.localtime(timezone.now()).time()
        
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if open_t == close_t: return False
        if open_t < close_t:
            return open_t <= check_time <= close_t
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, service, employee, target_date):
        """
        ALGORITMO MAESTRO DE DISPONIBILIDAD
        Cruza: Horario Negocio + Horario Empleado + Almuerzo + Duración Servicio
        """
        slots = []
        
        # 1. Verificar si el empleado trabaja ese día de la semana
        # 0=Lunes, 6=Domingo
        day_of_week = str(target_date.weekday())
        try:
            schedule = employee.schedule
            if day_of_week not in schedule.active_days.split(','):
                return [] # No trabaja hoy
        except:
            return [] # No tiene horario configurado

        # 2. Definir ventana de tiempo (Intersección Negocio vs Empleado)
        # El inicio es el MÁXIMO entre (Apertura Negocio, Entrada Empleado)
        start_hour = max(salon.opening_time, schedule.work_start)
        
        # El fin es el MÍNIMO entre (Cierre Negocio, Salida Empleado)
        # Nota simplificada: Asumimos por ahora que no hay turno nocturno cruzado para empleados
        # para no complicar la Fase 3, pero el sistema lo soporta si se ajusta.
        end_hour = min(salon.closing_time, schedule.work_end)
        
        if start_hour >= end_hour:
            return [] # Horarios incompatibles

        # Convertir a datetime para sumar minutos
        current_dt = datetime.combine(target_date, start_hour)
        end_dt = datetime.combine(target_date, end_hour)
        
        # Almuerzo
        lunch_start_dt = datetime.combine(target_date, schedule.lunch_start)
        lunch_end_dt = datetime.combine(target_date, schedule.lunch_end)

        # Duración total requerida (Servicio + Limpieza)
        duration = timedelta(minutes=service.duration_minutes + service.buffer_time)

        # 3. Iterar cada 30 min buscando huecos
        while current_dt + duration <= end_dt:
            slot_end = current_dt + duration
            is_valid = True
            
            # A. Validar Almuerzo (Si la cita choca con la hora de comida)
            # Choca si el fin de la cita es después del inicio del almuerzo 
            # Y el inicio de la cita es antes del fin del almuerzo
            if (slot_end > lunch_start_dt) and (current_dt < lunch_end_dt):
                is_valid = False
            
            # B. Validar Citas Existentes (Base de Datos)
            # (Aquí iría la consulta a Appointment.objects.filter(...) en Fase 4)
            
            # C. Agregar si es válido
            if is_valid:
                slots.append({
                    'time_obj': current_dt.time(),
                    'label': current_dt.strftime("%I:%M %p"),
                    'is_available': True 
                })
            
            current_dt += timedelta(minutes=30)
            
        return slots