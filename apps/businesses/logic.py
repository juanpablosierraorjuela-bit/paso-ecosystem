from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        """Verifica si el salón está abierto en el momento actual."""
        now_local = timezone.localtime(timezone.now())
        if not check_time:
            check_time = now_local.time()
        
        today_idx = str(now_local.weekday())
        if hasattr(salon, 'active_days') and salon.active_days:
            if today_idx not in salon.active_days.split(','):
                return False

        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if not open_t or not close_t or open_t == close_t:
            return False
        
        if open_t < close_t:
            return open_t <= check_time <= close_t
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, services_list, employee, target_date):
        """Genera slots con jerarquía: Semana (si tiene días) > Horario Base."""
        from apps.marketplace.models import Appointment
        from .models import EmployeeWeeklySchedule, EmployeeSchedule
        
        slots = []
        day_of_week = str(target_date.weekday())
        now_local = timezone.localtime(timezone.now())

        # 1. ¿Abre el salón?
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return []

        # 2. DETERMINAR HORARIO (JERARQUÍA CORREGIDA)
        iso_year, iso_week, _ = target_date.isocalendar()
        
        # Buscamos la configuración semanal
        weekly_config = EmployeeWeeklySchedule.objects.filter(
            employee=employee,
            year=iso_year,
            week_number=iso_week
        ).first()

        current_work_start = None
        current_work_end = None
        current_active_days = []

        # LA CLAVE: Solo entrar aquí si el registro existe Y TIENE DÍAS ACTIVOS
        # Si el registro existe pero active_days está vacío o es None, ignoramos la semana.
        if weekly_config and weekly_config.active_days and len(weekly_config.active_days.strip()) > 0:
            current_work_start = weekly_config.work_start
            current_work_end = weekly_config.work_end
            current_active_days = weekly_config.active_days.split(',')
        else:
            # FALLBACK: Usar Horario Base si la semana no está configurada realmente
            base_schedule = EmployeeSchedule.objects.filter(employee=employee).first()
            if base_schedule and base_schedule.active_days:
                current_work_start = base_schedule.work_start
                current_work_end = base_schedule.work_end
                current_active_days = base_schedule.active_days.split(',')
            else:
                return [] # No hay horario de ningún tipo

        # 3. ¿Trabaja hoy el empleado?
        if day_of_week not in current_active_days:
            return []
            
        if not current_work_start or not current_work_end:
            return []

        # 4. Citas existentes
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').prefetch_related('services')

        # 5. Intersección Salón vs Empleado
        start_hour = max(salon.opening_time, current_work_start)
        end_hour = min(salon.closing_time, current_work_end)
        
        if start_hour >= end_hour:
            return []

        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        
        total_duration_mins = sum(s.duration_minutes for s in services_list)
        service_duration = timedelta(minutes=total_duration_mins)

        # 6. Generar slots
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            if target_date == now_local.date():
                if slot_start <= now_local + timedelta(minutes=30):
                    is_valid = False
            
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
                    'time_obj': slot_start.time(),
                    'time': slot_start.strftime("%H:%M"),
                    'label': slot_start.strftime("%I:%M %p"),
                    'is_available': True 
                })
            
            current_dt += timedelta(minutes=30)
            
        return slots