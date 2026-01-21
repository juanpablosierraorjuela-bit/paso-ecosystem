from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        """Verifica si el salón está abierto en el momento actual o una hora dada."""
        now_local = timezone.localtime(timezone.now())
        if not check_time:
            check_time = now_local.time()
        
        # 1. ¿Abre el salón hoy? (Basado en active_days del Salón)
        today_idx = str(now_local.weekday())
        if hasattr(salon, 'active_days') and salon.active_days:
            if today_idx not in salon.active_days.split(','):
                return False

        # 2. Validar Rango de Horas del Salón
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
        """
        Genera slots de tiempo disponibles.
        ESTRICTO: Si no hay configuración semanal explícita con días activos, devuelve vacío.
        """
        from apps.marketplace.models import Appointment
        from .models import EmployeeWeeklySchedule
        
        slots = []
        day_of_week = str(target_date.weekday())
        now_local = timezone.localtime(timezone.now())

        # 1. Filtro del Salón: Si el negocio cierra ese día de la semana, nadie trabaja.
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return []

        # 2. BUSCAR HORARIO DEL EMPLEADO (ESTRICTO POR SEMANA ISO)
        iso_year, iso_week, _ = target_date.isocalendar()
        
        weekly_config = EmployeeWeeklySchedule.objects.filter(
            employee=employee,
            year=iso_year,
            week_number=iso_week
        ).first()

        # REGLA DE ORO: Si no existe la configuración O si active_days está vacío/nulo,
        # significa que el empleado NO ha habilitado esa semana. No hay disponibilidad.
        if not weekly_config or not weekly_config.active_days:
            return []

        current_active_days = weekly_config.active_days.split(',')
        
        # 3. Validar si el empleado marcó este día específico como activo
        if day_of_week not in current_active_days:
            return []
            
        current_work_start = weekly_config.work_start
        current_work_end = weekly_config.work_end

        if not current_work_start or not current_work_end:
            return []

        # 4. Obtener citas ya reservadas para calcular huecos
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').prefetch_related('services')

        # 5. Intersección de horarios (Salón vs Empleado)
        # El empleado no puede empezar antes que el salón ni terminar después
        start_hour = max(salon.opening_time, current_work_start)
        end_hour = min(salon.closing_time, current_work_end)
        
        # Si el inicio es después del fin, no hay rango válido
        if start_hour >= end_hour:
            return []

        # Preparar objetos datetime para el bucle
        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        
        # Calcular duración total del servicio solicitado
        total_duration_mins = sum(s.duration_minutes for s in services_list)
        service_duration = timedelta(minutes=total_duration_mins)

        # 6. Generar los slots cada 30 min
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            # Restricción: No mostrar horas pasadas si es el día de hoy (con margen de 30min)
            if target_date == now_local.date():
                if slot_start <= now_local + timedelta(minutes=30):
                    is_valid = False
            
            # Restricción: No solapar con citas existentes
            if is_valid:
                for app in existing_appointments:
                    app_start = app.date_time
                    # Calculamos fin de la cita existente
                    app_total_min = sum(s.duration_minutes for s in app.services.all())
                    app_end = app_start + timedelta(minutes=app_total_min)
                    
                    # Lógica de solapamiento: (StartA < EndB) y (EndA > StartB)
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