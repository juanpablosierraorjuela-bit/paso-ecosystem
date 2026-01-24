from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None, target_date=None):
        """
        Verifica si el salón está abierto en un momento específico.
        Si no se pasa target_date, usa la fecha local actual.
        """
        now_local = timezone.localtime(timezone.now())
        current_date = target_date if target_date else now_local.date()
        
        if not check_time:
            check_time = now_local.time()
        
        # 1. ¿Abre el salón este día de la semana?
        day_idx = str(current_date.weekday())
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_idx not in salon.active_days.split(','):
                return False

        # 2. Validar Rango de Horas del Salón
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if not open_t or not close_t or open_t == close_t:
            return False
            
        # Caso horario normal (ej: 08:00 a 20:00)
        if open_t < close_t:
            return open_t <= check_time <= close_t
        # Caso horario nocturno (ej: 22:00 a 02:00)
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, services_list, employee, target_date):
        """
        Genera slots de disponibilidad considerando:
        1. Horario del Salón.
        2. Horario Semanal del Empleado (EmployeeWeeklySchedule).
        3. Horario de Almuerzo del Empleado.
        4. Citas existentes.
        5. Margen de 30 min para citas en el día actual.
        """
        from apps.marketplace.models import Appointment
        from .models import EmployeeWeeklySchedule
        
        slots = []
        day_of_week = str(target_date.weekday())
        now_local = timezone.localtime(timezone.now())

        # 1. Filtro del Salón (Si el salón cierra, no hay slots)
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return []

        # 2. Obtener configuración semanal del empleado
        iso_year, iso_week, _ = target_date.isocalendar()
        weekly_config = EmployeeWeeklySchedule.objects.filter(
            employee=employee,
            year=iso_year,
            week_number=iso_week
        ).first()

        # Si no hay configuración o no trabaja este día, retornamos vacío
        if not weekly_config or not weekly_config.active_days:
            return []

        active_days_list = weekly_config.active_days.split(',')
        if day_of_week not in active_days_list:
            return []

        # 3. Determinar el rango de trabajo (Intersección Salón vs Empleado)
        # Usamos max/min para asegurar que el empleado no trabaje si el salón está cerrado
        start_hour = max(salon.opening_time, weekly_config.work_start)
        end_hour = min(salon.closing_time, weekly_config.work_end)
        
        if start_hour >= end_hour:
            return []

        # 4. Preparar datos para el bucle
        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        
        total_duration_mins = sum(s.duration_minutes for s in services_list)
        service_duration = timedelta(minutes=total_duration_mins)

        # 5. Citas existentes (pre-procesadas para mejorar rendimiento)
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').prefetch_related('services')

        booked_intervals = []
        for app in existing_appointments:
            app_duration = sum(s.duration_minutes for s in app.services.all())
            booked_intervals.append({
                'start': app.date_time,
                'end': app.date_time + timedelta(minutes=app_duration)
            })

        # 6. Definir periodos de descanso (Almuerzo)
        lunch_start = None
        lunch_end = None
        if weekly_config.lunch_start and weekly_config.lunch_end:
            lunch_start = timezone.make_aware(datetime.combine(target_date, weekly_config.lunch_start))
            lunch_end = timezone.make_aware(datetime.combine(target_date, weekly_config.lunch_end))

        # 7. Generar slots cada 30 minutos
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            # A. No permitir citas en el pasado (con margen de seguridad de 30 min)
            if target_date == now_local.date():
                if slot_start <= now_local + timedelta(minutes=30):
                    is_valid = False
            
            # B. Validar contra el Horario de Almuerzo
            if is_valid and lunch_start and lunch_end:
                # El slot es inválido si se solapa con el almuerzo
                if (slot_start < lunch_end) and (slot_end > lunch_start):
                    is_valid = False
            
            # C. Validar contra Citas Existentes
            if is_valid:
                for interval in booked_intervals:
                    if (slot_start < interval['end']) and (slot_end > interval['start']):
                        is_valid = False
                        break
            
            # D. Agregar slot si pasó todas las pruebas
            if is_valid:
                slots.append({
                    'time_obj': slot_start.time(),
                    'time': slot_start.strftime("%H:%M"),
                    'label': slot_start.strftime("%I:%M %p"),
                    'is_available': True 
                })
            
            # Siguiente posibilidad cada 30 minutos
            current_dt += timedelta(minutes=30)
            
        return slots