from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# --- CORRECCIÓN DE IMPORTACIONES ---
# Antes buscaba en .models (users), ahora busca en la app correcta (businesses)
from apps.businesses.models import Salon
from apps.businesses.forms import SalonCreateForm

def home(request):
    """Muestra la lista de salones en la página de inicio"""
    # Filtramos solo los que tengan datos básicos para no mostrar vacíos
    salons = Salon.objects.all().order_by('-id')
    return render(request, 'home.html', {'salons': salons})

@login_required
def dashboard_view(request):
    """
    Controlador de tráfico:
    1. ¿Es dueño? -> ¿Tiene salón? -> Si no, mandar a crear. Si sí, mostrar panel.
    2. ¿Es empleado? -> Mostrar panel de empleado.
    """
    user = request.user

    # Verificamos si es dueño (ADMIN) o tiene el flag is_business_owner
    # Usamos getattr para evitar errores si el campo aún no existe en la BD
    is_owner = getattr(user, 'role', '') == 'ADMIN' or getattr(user, 'is_business_owner', False)

    if is_owner:
        # Buscamos si este usuario ya tiene un salón registrado
        salon = Salon.objects.filter(owner=user).first()
        
        if not salon:
            # SI ES DUEÑO PERO NO TIENE SALÓN -> REDIRIGIR A CREARLO
            return redirect('create_salon')
        
        # SI YA TIENE SALÓN -> MOSTRAR DASHBOARD DE NEGOCIO
        return render(request, 'dashboard/index.html', {'salon': salon})

    # Caso 2: Empleado o Cliente (pendiente de implementar lógica completa)
    return render(request, 'dashboard/employee_dashboard.html')

@login_required
def create_salon_view(request):
    """Vista para que el dueño registre su peluquería por primera vez"""
    # Si ya tiene salón, lo sacamos de aquí para evitar duplicados
    if Salon.objects.filter(owner=request.user).exists():
        return redirect('dashboard')

    if request.method == 'POST':
        form = SalonCreateForm(request.POST, request.FILES)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.owner = request.user
            salon.save()
            return redirect('dashboard')
    else:
        form = SalonCreateForm()

    return render(request, 'dashboard/create_salon.html', {'form': form})

def salon_detail(request, slug):
    """Vista pública del perfil del salón"""
    salon = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': salon})