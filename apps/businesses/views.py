from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .models import Salon, OpeningHours
from .forms import SalonCreateForm, OpeningHoursForm

@login_required
def salon_settings_view(request):
    """
    Vista de Configuración del Salón:
    Permite editar la info del negocio Y los horarios de apertura en una sola pantalla.
    """
    # Buscar el salón del usuario logueado
    salon = get_object_or_404(Salon, owner=request.user)
    
    # 1. AUTOGENERAR HORARIOS SI NO EXISTEN
    # Si el salón es nuevo, creamos los 7 días por defecto (Lunes=0 ... Domingo=6)
    if salon.opening_hours.count() < 7:
        for i in range(7):
            OpeningHours.objects.get_or_create(
                salon=salon, 
                weekday=i, 
                defaults={'from_hour': '09:00', 'to_hour': '18:00', 'is_closed': False}
            )

    # 2. CONFIGURAR EL "FORMSET" (Permite editar 7 formularios de horario a la vez)
    # extra=0 para no agregar filas vacías, solo mostrar las 7 existentes
    HoursFormSet = modelformset_factory(OpeningHours, form=OpeningHoursForm, extra=0)
    
    if request.method == 'POST':
        salon_form = SalonCreateForm(request.POST, request.FILES, instance=salon)
        hours_formset = HoursFormSet(request.POST, queryset=salon.opening_hours.all())
        
        if salon_form.is_valid() and hours_formset.is_valid():
            salon_form.save()
            hours_formset.save()
            return redirect('dashboard') # Guardar y volver al panel
    else:
        salon_form = SalonCreateForm(instance=salon)
        hours_formset = HoursFormSet(queryset=salon.opening_hours.all())

    return render(request, 'dashboard/settings.html', {
        'salon_form': salon_form,
        'hours_formset': hours_formset,
        'salon': salon
    })