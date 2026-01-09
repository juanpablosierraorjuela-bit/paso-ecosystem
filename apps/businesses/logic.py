from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        if not check_time:
            check_time = timezone.localtime(timezone.now()).time()
        
        # 1. Validar Día de la Semana
        today_idx = str(timezone.localtime(timezone.now()).weekday())
        if hasattr(salon, 'active_days') and salon.active_days:
            if today_idx not in salon.active_days.split(','):
                return False

        # 2. Validar Hora
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if open_t == close_t: return False
        if open_t < close_t:
            return open_t <= check_time <= close_t
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, service, employee, target_date):
        slots = []
        day_of_week = str(target_date.weekday())

        # 1. FILTRO SUPREMO: ¿El Negocio abre hoy?
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return [] # Negocio cerrado hoy

        # 2. ¿El Empleado trabaja hoy?
        try:
            schedule = employee.schedule
            if day_of_week not in schedule.active_days.split(','):
                return [] # Empleado descansa hoy
        except:
            return []

        # 3. Definir ventana de tiempo (Intersección)
        start_hour = max(salon.opening_time, schedule.work_start)
        end_hour = min(salon.closing_time, schedule.work_end)
        
        if start_hour >= end_hour:
            return []

        current_dt = datetime.combine(target_date, start_hour)
        end_dt = datetime.combine(target_date, end_hour)
        lunch_start_dt = datetime.combine(target_date, schedule.lunch_start)
        lunch_end_dt = datetime.combine(target_date, schedule.lunch_end)
        duration = timedelta(minutes=service.duration_minutes + service.buffer_time)

        while current_dt + duration <= end_dt:
            slot_end = current_dt + duration
            is_valid = True
            
            if (slot_end > lunch_start_dt) and (current_dt < lunch_end_dt):
                is_valid = False
            
            # Aquí se conectará la validación de citas existentes (Appointment)
            
            if is_valid:
                slots.append({
                    'time_obj': current_dt.time(),
                    'label': current_dt.strftime("%I:%M %p"),
                    'is_available': True 
                })
            
            current_dt += timedelta(minutes=30)
            
        return slots