from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        """Verifica si el salón está abierto en el momento actual o una hora dada."""
        now_local = timezone.localtime(timezone.now())
        if not check_time:
            check_time = now_local.time()
        
        # Validar Día de la Semana del Salón
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
    def get_available_slots(salon, service, employee, target_date):
        """Genera slots de tiempo inteligentes validando todas las reglas de negocio."""
        # Importación local para evitar importación circular
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
            return [] # El empleado no tiene horario configurado

        # 3. Obtener citas ya reservadas para este empleado en esta fecha
        # Excluimos las canceladas para liberar el tiempo
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').select_related('service')

        # 4. Definir ventana de tiempo (Intersección Salón y Empleado)
        start_hour = max(salon.opening_time, schedule.work_start)
        end_hour = min(salon.closing_time, schedule.work_end)
        
        if start_hour >= end_hour:
            return []

        # Convertimos a datetimes "aware" (con zona horaria) para comparaciones precisas
        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        lunch_start_dt = timezone.make_aware(datetime.combine(target_date, schedule.lunch_start))
        lunch_end_dt = timezone.make_aware(datetime.combine(target_date, schedule.lunch_end))
        
        # Duración total: Tiempo del servicio + tiempo de limpieza (buffer)
        service_duration = timedelta(minutes=service.duration_minutes + service.buffer_time)

        # 5. Generar y Validar cada Slot
        # El bucle asegura que el servicio quepa antes de que cierre el negocio
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            # REGLA A: No mostrar horas que ya pasaron (si es hoy)
            if target_date == now_local.date() and slot_start <= now_local:
                is_valid = False
            
            # REGLA B: No debe cruzarse con el almuerzo del empleado
            if is_valid:
                if (slot_end > lunch_start_dt) and (slot_start < lunch_end_dt):
                    is_valid = False
            
            # REGLA C: No debe cruzarse con citas ya existentes
            if is_valid:
                for app in existing_appointments:
                    app_start = app.date_time
                    # Calculamos duración de la cita existente
                    app_total_min = app.service.duration_minutes + app.service.buffer_time
                    app_end = app_start + timedelta(minutes=app_total_min)
                    
                    # Lógica de colisión (traslape de intervalos)
                    if (slot_start < app_end) and (slot_end > app_start):
                        is_valid = False
                        break
            
            if is_valid:
                slots.append({
                    'time_obj': slot_start.time(),
                    'label': slot_start.strftime("%I:%M %p"),
                    'is_available': True 
                })
            
            # Avanzar el puntero 30 minutos para ofrecer el siguiente slot disponible
            current_dt += timedelta(minutes=30)
            
        return slots