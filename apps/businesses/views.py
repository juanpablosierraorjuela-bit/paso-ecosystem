from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Salon
from .forms import SalonCreateForm # Lo crearemos en el siguiente paso

def home(request):
    """Vista principal: Muestra todos los salones disponibles"""
    salons = Salon.objects.all()
    return render(request, 'home.html', {'salons': salons})

@login_required
def dashboard_view(request):
    """
    Controlador de tráfico:
    - Si el usuario no tiene salón, lo obliga a crear uno.
    - Si ya tiene, le muestra su panel.
    """
    user = request.user

    # 1. Verificar si es dueño
    if user.is_business_owner:
        # Intentar obtener el salón del usuario
        # Asumiendo que la relación en models.py es OneToOne o ForeignKey
        # Si tu modelo User no tiene 'salon', usamos la relación inversa.
        salon = Salon.objects.filter(owner=user).first()

        if not salon:
            # SI NO TIENE SALÓN -> REDIRIGIR A CREARLO
            return redirect('create_salon')
        
        # SI YA TIENE SALÓN -> MOSTRAR DASHBOARD
        return render(request, 'dashboard/index.html', {'salon': salon})

    # 2. Lógica para empleados (si aplica)
    return render(request, 'dashboard/employee_dashboard.html')

@login_required
def create_salon_view(request):
    """Vista para registrar el negocio por primera vez"""
    # Si ya tiene salón, no debería estar aquí
    if Salon.objects.filter(owner=request.user).exists():
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.owner = request.user # Asignar el dueño actual
            salon.save()
            return redirect('dashboard')
    else:
        form = SalonCreateForm()

    return render(request, 'dashboard/create_salon.html', {'form': form})