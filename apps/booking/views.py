from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, EmployeeSchedule
from apps.businesses.models import OperatingHour
from .forms import EmployeeScheduleForm, EmployeeProfileForm

@login_required
def employee_dashboard(request):
    # Citas verificadas
    appointments = Appointment.objects.filter(
        employee=request.user,
        status='VERIFIED'
    ).order_by('date', 'start_time')
    return render(request, 'booking/employee_dashboard.html', {'appointments': appointments})

@login_required
def employee_schedule(request):
    employee = request.user
    workplace = employee.workplace
    
    if not workplace:
        messages.error(request, "No tienes un negocio asignado. Contacta a tu jefe.")
        return redirect('booking:employee_dashboard')

    # Asegurar que existan los 7 días de horario para el empleado
    if not employee.schedules.exists():
        for day_code, _ in OperatingHour.DAYS:
            EmployeeSchedule.objects.create(
                employee=employee,
                business=workplace,
                day_of_week=day_code,
                start_time="09:00",
                end_time="18:00"
            )

    # Traemos los horarios del EMPLEADO y del NEGOCIO para cruzar la info
    emp_schedules = employee.schedules.all().order_by('day_of_week')
    biz_hours = workplace.operating_hours.all()
    # Creamos un dict para acceso rápido: biz_hours_map[0] = Horario Lunes
    biz_hours_map = {h.day_of_week: h for h in biz_hours}

    if request.method == 'POST':
        # Procesamiento simple del formulario manual
        for schedule in emp_schedules:
            day = schedule.day_of_week
            
            # Solo procesar si el negocio abre ese día
            if not biz_hours_map.get(day).is_closed:
                prefix = f"day_{day}"
                
                # Checkbox de Activo
                is_active = request.POST.get(f"{prefix}_active") == 'on'
                schedule.is_active_day = is_active
                
                if is_active:
                    schedule.start_time = request.POST.get(f"{prefix}_start")
                    schedule.end_time = request.POST.get(f"{prefix}_end")
                    
                    # Breaks (Opcionales)
                    b_start = request.POST.get(f"{prefix}_break_start")
                    b_end = request.POST.get(f"{prefix}_break_end")
                    if b_start and b_end:
                        schedule.break_start = b_start
                        schedule.break_end = b_end
                    else:
                        schedule.break_start = None
                        schedule.break_end = None
                
                schedule.save()
        
        messages.success(request, "Tu horario ha sido actualizado.")
        return redirect('booking:employee_schedule')

    # Preparamos los datos combinados para el template
    combined_schedule = []
    for emp_sch in emp_schedules:
        biz_h = biz_hours_map.get(emp_sch.day_of_week)
        combined_schedule.append({
            'employee': emp_sch,
            'business': biz_h
        })

    return render(request, 'booking/schedule.html', {'combined_schedule': combined_schedule})

@login_required
def employee_profile(request):
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('booking:employee_profile')
    else:
        form = EmployeeProfileForm(instance=request.user)
    
    return render(request, 'booking/profile.html', {'form': form})

@login_required
def client_dashboard(request):
    return render(request, 'booking/client_dashboard.html')
