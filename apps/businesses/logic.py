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
        # Importamos el modelo de semanas aquí para evitar errores de importación circular
        from .models import EmployeeWeeklySchedule
        
        slots = []
        day_of_week = str(target_date.weekday()) # 0=Lunes, 6=Domingo
        now_local = timezone.localtime(timezone.now())

        # 1. Filtro del Dueño: ¿El Salón abre este día?
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return []

        # 2. DETERMINAR HORARIO DEL EMPLEADO (Base vs Semanal)
        # Calculamos qué semana del año es la fecha solicitada
        iso_year, iso_week, _ = target_date.isocalendar()

        # Buscamos si hay una configuración específica para esa semana
        weekly_config = EmployeeWeeklySchedule.objects.filter(
            employee=employee,
            year=iso_year,
            week_number=iso_week
        ).first()

        # Variables de trabajo (se llenarán con el horario semanal o el base)
        current_work_start = None
        current_work_end = None
        current_lunch_start = None
        current_lunch_end = None
        current_active_days = []

        if weekly_config:
            # Opción A: Usar horario específico de la semana
            current_work_start = weekly_config.work_start
            current_work_end = weekly_config.work_end
            current_lunch_start = weekly_config.lunch_start
            current_lunch_end = weekly_config.lunch_end
            current_active_days = weekly_config.active_days.split(',')
        else:
            # Opción B: Usar horario base (default)
            try:
                base_schedule = employee.schedule
                current_work_start = base_schedule.work_start
                current_work_end = base_schedule.work_end
                current_lunch_start = base_schedule.lunch_start
                current_lunch_end = base_schedule.lunch_end
                current_active_days = base_schedule.active_days.split(',')
            except:
                # Si el empleado no tiene horario configurado, no mostramos nada
                return []

        # Filtro del Empleado: ¿Trabaja este día según la configuración vigente?
        if day_of_week not in current_active_days:
            return []

        # 3. Citas ya reservadas (Pre-cargamos servicios para rapidez)
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').prefetch_related('services')

        # 4. INTERSECCIÓN DE HORARIOS (Salon vs Empleado)
        # Usamos las variables 'current_' definidas arriba
        start_hour = max(salon.opening_time, current_work_start)
        end_hour = min(salon.closing_time, current_work_end)
        
        if start_hour >= end_hour:
            return []

        # Convertimos a objetos datetime conscientes de zona horaria
        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        
        lunch_start_dt = timezone.make_aware(datetime.combine(target_date, current_lunch_start))
        lunch_end_dt = timezone.make_aware(datetime.combine(target_date, current_lunch_end))
        
        # CÁLCULO DE DURACIÓN TOTAL DEL COMBO
        total_duration_mins = sum(s.duration_minutes + s.buffer_time for s in services_list)
        service_duration = timedelta(minutes=total_duration_mins)

        # 5. Generar y Validar cada Slot
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            # Regla A: No mostrar horas pasadas (si es hoy)
            if target_date == now_local.date() and slot_start <= now_local:
                is_valid = False
            
            # Regla B: Almuerzo (El bloque completo no debe tocar el almuerzo definido para esta semana)
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