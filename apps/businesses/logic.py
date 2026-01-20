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
        # Importamos el modelo de semanas aquí para evitar errores de importación circular
        from .models import EmployeeWeeklySchedule, EmployeeSchedule
        
        slots = []
        day_of_week = str(target_date.weekday()) # 0=Lunes, 6=Domingo
        now_local = timezone.localtime(timezone.now())

        # 1. Filtro del Dueño: ¿El Salón abre este día?
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return []

        # 2. DETERMINAR HORARIO DEL EMPLEADO (PRIORIDAD: Semanal > Base)
        # Calculamos qué semana del año es la fecha solicitada
        iso_year, iso_week, _ = target_date.isocalendar()

        # A. Buscamos si hay una configuración específica para esa semana
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
            # Opción A: Usar horario específico de la semana (Si existe el registro)
            current_work_start = weekly_config.work_start
            current_work_end = weekly_config.work_end
            # Si active_days es None o vacío, asumimos que no trabaja, si tiene datos, hacemos split
            current_active_days = weekly_config.active_days.split(',') if weekly_config.active_days else []
        else:
            # Opción B: Usar horario base (default)
            try:
                # Buscamos el horario base explícitamente
                base_schedule = EmployeeSchedule.objects.filter(employee=employee).first()
                if base_schedule:
                    current_work_start = base_schedule.work_start
                    current_work_end = base_schedule.work_end
                    current_active_days = base_schedule.active_days.split(',') if base_schedule.active_days else []
                else:
                    return [] # No tiene horario configurado
            except:
                return []

        # Filtro del Empleado: ¿Trabaja este día según la configuración vigente?
        if day_of_week not in current_active_days:
            return []
            
        # Validación extra: Si por alguna razón start o end son None
        if not current_work_start or not current_work_end:
            return []

        # 3. Citas ya reservadas (Pre-cargamos servicios para rapidez)
        existing_appointments = Appointment.objects.filter(
            employee=employee,
            date_time__date=target_date
        ).exclude(status='CANCELLED').prefetch_related('services')

        # 4. INTERSECCIÓN DE HORARIOS (Salon vs Empleado)
        # El empleado no puede trabajar antes de que abra el salón ni después de que cierre
        start_hour = max(salon.opening_time, current_work_start)
        end_hour = min(salon.closing_time, current_work_end)
        
        if start_hour >= end_hour:
            return []

        # Convertimos a objetos datetime conscientes de zona horaria para iterar
        current_dt = timezone.make_aware(datetime.combine(target_date, start_hour))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_hour))
        
        # CÁLCULO DE DURACIÓN TOTAL DEL COMBO
        total_duration_mins = sum(s.duration_minutes for s in services_list) # + s.buffer_time si usas buffer
        service_duration = timedelta(minutes=total_duration_mins)

        # 5. Generar y Validar cada Slot
        while current_dt + service_duration <= end_dt:
            slot_start = current_dt
            slot_end = current_dt + service_duration
            is_valid = True
            
            # Regla A: No mostrar horas pasadas (si es hoy)
            if target_date == now_local.date():
                # Damos un margen de 30 min para no reservar "ya mismo"
                if slot_start <= now_local + timedelta(minutes=30):
                    is_valid = False
            
            # Regla B: Colisión con otras citas
            if is_valid:
                for app in existing_appointments:
                    app_start = app.date_time
                    # Sumamos duración de la cita existente
                    app_total_min = sum(s.duration_minutes for s in app.services.all())
                    app_end = app_start + timedelta(minutes=app_total_min)
                    
                    # Lógica de solapamiento: (StartA < EndB) y (EndA > StartB)
                    if (slot_start < app_end) and (slot_end > app_start):
                        is_valid = False
                        break
            
            if is_valid:
                slots.append({
                    'time_obj': slot_start.time(), # Para uso interno si se requiere
                    'time': slot_start.strftime("%H:%M"), # Para el value del input
                    'label': slot_start.strftime("%I:%M %p"), # Para mostrar al usuario
                    'is_available': True 
                })
            
            # Intervalo entre slots (ej. cada 30 min)
            current_dt += timedelta(minutes=30)
            
        return slots