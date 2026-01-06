from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import Booking

def cleanup_expired_bookings():
    limit_time = timezone.now() - timedelta(minutes=50)
    expired = Booking.objects.filter(status='PENDING_PAYMENT', created_at__lt=limit_time)
    expired.update(status='CANCELLED')

def get_available_slots(employee, service, date_obj):
    cleanup_expired_bookings()
    salon = employee.salon
    day_name = date_obj.strftime('%A').lower()
    salon_works = getattr(salon, f"work_{day_name}", False)
    if not salon_works: return []
    schedule_str = getattr(employee.schedule, f"{day_name}_hours", "CERRADO")
    if schedule_str == "CERRADO": return []
    try:
        emp_start_s, emp_end_s = schedule_str.split('-')
        emp_start = datetime.strptime(emp_start_s, "%H:%M").time()
        emp_end = datetime.strptime(emp_end_s, "%H:%M").time()
    except: return []
    real_start = max(emp_start, salon.opening_time)
    real_end = min(emp_end, salon.closing_time)
    if real_start >= real_end: return []
    block_minutes = service.duration + service.buffer_time
    bookings = Booking.objects.filter(employee=employee, date_time__date=date_obj).exclude(status='CANCELLED')
    available_slots = []
    current_time = datetime.combine(date_obj, real_start)
    limit_time = datetime.combine(date_obj, real_end)
    while current_time + timedelta(minutes=block_minutes) <= limit_time:
        slot_end = current_time + timedelta(minutes=block_minutes)
        is_viable = True
        for b in bookings:
            if current_time < b.end_time and slot_end > b.date_time:
                is_viable = False
                break
        if is_viable: available_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)
    return available_slots
