from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        """Verifica si el salón está abierto en el momento actual o una hora dada."""
        now_local = timezone.localtime(timezone.now())
        if not check_time:
            check_time = now_local.time()
        
        # Validar Día de la Semana del Salón (Filtro Maestro)
        today_idx = str(now_local.weekday())
        if hasattr(salon, 'active_days') and salon.active_days:
            if today_idx not in salon.active_days.split(','):
                return False

        # Validar Rango de Horas
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if open_t == close_t: return False
        if open_t < close_t:
            return open_t <= check_time <= close_t
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, services_list, employee, target_date):
        """Genera slots validando un bloque de tiempo continuo para múltiples servicios."""
        from apps.marketplace.models import Appointment
        
        slots = []
        day_of_week = str(target_date.weekday())
        now_local = timezone.localtime(timezone.now())

        # 1. Filtro del Dueño: ¿El Salón abre este día?
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return []

        # 2. Filtro del Empleado: ¿El Especialista trabaja este día?
        try:
            schedule = employee.schedule
            if day_of_week not in schedule.active_days.split(','):
                return []
        except:
            return []

        # 3. Citas ya reservadas (Pre-cargamos servicios para rapidez)
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').prefetch_related('services')

        # 4. INTERSECCIÓN DE HORARIOS
        start_hour = max(salon.opening_time, schedule.work_start)
        end_hour = min(salon.closing_time, schedule.work_end)
        
        if start_hour >= end_hour:
            return []

        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        lunch_start_dt = timezone.make_aware(datetime.combine(target_date, schedule.lunch_start))
        lunch_end_dt = timezone.make_aware(datetime.combine(target_date, schedule.lunch_end))
        
        # CÁLCULO DE DURACIÓN TOTAL DEL COMBO
        total_duration_mins = sum(s.duration_minutes + s.buffer_time for s in services_list)
        service_duration = timedelta(minutes=total_duration_mins)

        # 5. Generar y Validar cada Slot
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            # Regla A: No mostrar horas pasadas
            if target_date == now_local.date() and slot_start <= now_local:
                is_valid = False
            
            # Regla B: Almuerzo (El bloque completo no debe tocar el almuerzo)
            if is_valid:
                if (slot_end > lunch_start_dt) and (slot_start < lunch_end_dt):
                    is_valid = False
            
            # Regla C: Colisión con otras citas
            if is_valid:
                for app in existing_appointments:
                    app_start = app.date_time
                    # Sumamos duración de la cita existente
                    app_total_min = sum(s.duration_minutes + s.buffer_time for s in app.services.all())
                    app_end = app_start + timedelta(minutes=app_total_min)
                    
                    if (slot_start < app_end) and (slot_end > app_start):
                        is_valid = False
                        break
            
            if is_valid:
                slots.append({
                    'time_obj': slot_start.time(),
                    'label': slot_start.strftime("%I:%M %p"),
                    'is_available': True 
                })
            
            current_dt += timedelta(minutes=30)
            
        return slots