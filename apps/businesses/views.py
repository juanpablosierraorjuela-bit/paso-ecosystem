from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def owner_dashboard(request):
    # Aquí iría la lógica del Temporizador y Métricas
    return render(request, 'businesses/dashboard.html')

@login_required
def services_list(request):
    # Lógica para listar y crear servicios
    return render(request, 'businesses/services.html')

@login_required
def employees_list(request):
    # Lógica para gestionar empleados
    return render(request, 'businesses/employees.html')

@login_required
def schedule_config(request):
    # Lógica de Horarios (Apertura, Cierre, Turnos Nocturnos)
    return render(request, 'businesses/schedule.html')

@login_required
def business_settings(request):
    # Configuración del Negocio (Redes, Pagos, Abonos)
    return render(request, 'businesses/settings.html')
