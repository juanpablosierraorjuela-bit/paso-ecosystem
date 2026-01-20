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
        
        if not open_t or not close_t:
            return False
            
        if open_t == close_t: return False
        
        if open_t < close_t:
            return open_t <= check_time <= close_t
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, services_list, employee, target_date):
        """Genera slots validando un bloque de tiempo continuo para múltiples servicios."""
        from apps.marketplace.models import Appointment
        # Importamos los modelos necesarios dentro del método para evitar ciclos
        from .models import EmployeeWeeklySchedule, EmployeeSchedule
        
        slots = []
        day_of_week = str(target_date.weekday()) # 0=Lunes, 6=Domingo
        now_local = timezone.localtime(timezone.now())

        # 1. Filtro del Dueño: ¿El Salón abre este día?
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return []

        # 2. DETERMINAR HORARIO DEL EMPLEADO (PRIORIDAD: Semanal > Base)
        iso_year, iso_week, _ = target_date.isocalendar()

        # A. Buscamos si hay una configuración específica para esa semana (La corrección clave)
        weekly_config = EmployeeWeeklySchedule.objects.filter(
            employee=employee,
            year=iso_year,
            week_number=iso_week
        ).first()

        # Variables de trabajo
        current_work_start = None
        current_work_end = None
        current_active_days = []

        if weekly_config:
            # Opción A: Usar horario específico de la semana modificado por el empleado
            current_work_start = weekly_config.work_start
            current_work_end = weekly_config.work_end
            current_active_days = weekly_config.active_days.split(',') if weekly_config.active_days else []
        else:
            # Opción B: Usar horario base (default)
            try:
                base_schedule = EmployeeSchedule.objects.filter(employee=employee).first()
                if base_schedule:
                    current_work_start = base_schedule.work_start
                    current_work_end = base_schedule.work_end
                    current_active_days = base_schedule.active_days.split(',') if base_schedule.active_days else []
                else:
                    return [] # El empleado no tiene horario configurado
            except:
                return []

        # Filtro del Empleado: ¿Trabaja este día según la configuración vigente?
        if day_of_week not in current_active_days:
            return []
            
        if not current_work_start or not current_work_end:
            return []

        # 3. Citas ya reservadas
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').prefetch_related('services')

        # 4. INTERSECCIÓN DE HORARIOS (Salon vs Empleado)
        start_hour = max(salon.opening_time, current_work_start)
        end_hour = min(salon.closing_time, current_work_end)
        
        if start_hour >= end_hour:
            return []

        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        
        # Cálculo duración total
        total_duration_mins = sum(s.duration_minutes for s in services_list)
        service_duration = timedelta(minutes=total_duration_mins)

        # 5. Generar slots
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            # Regla A: No mostrar horas pasadas (si es hoy)
            if target_date == now_local.date():
                if slot_start <= now_local + timedelta(minutes=30):
                    is_valid = False
            
            # Regla B: Colisión con otras citas
            if is_valid:
                for app in existing_appointments:
                    app_start = app.date_time
                    app_total_min = sum(s.duration_minutes for s in app.services.all())
                    app_end = app_start + timedelta(minutes=app_total_min)
                    
                    if (slot_start < app_end) and (slot_end > app_start):
                        is_valid = False
                        break
            
            if is_valid:
                slots.append({
                    # Enviamos strings formateados para evitar errores en views.py
                    'time': slot_start.strftime("%H:%M"), 
                    'label': slot_start.strftime("%I:%M %p"), 
                    'is_available': True 
                })
            
            current_dt += timedelta(minutes=30)
            
        return slots