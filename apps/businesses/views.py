from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings

@login_required
def owner_dashboard(request):
    # Seguridad: Solo dueños
    if request.user.role != 'OWNER':
        return redirect('home')
    
    # Obtener Salón
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner') # Si por error no tiene salón

    # Lógica del Temporizador (The Reaper)
    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = int(remaining_time.total_seconds())
    
    if total_seconds_left < 0:
        total_seconds_left = 0

    # Lógica de WhatsApp
    admin_settings = GlobalSettings.objects.first()
    admin_phone = admin_settings.whatsapp_support if admin_settings else '573000000000' # Fallback
    
    wa_message = f"Hola PASO, quiero activar mi ecosistema. Soy el Negocio: {salon.name} (ID Usuario: {request.user.id}). Adjunto mi comprobante de $50.000."
    wa_link = f"https://wa.me/{admin_phone}?text={wa_message}"

    context = {
        'salon': salon,
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment
    }
    return render(request, 'businesses/dashboard.html', context)

# --- Vistas Placeholder para el futuro (Evita errores 404) ---
@login_required
def services_list(request):
    return render(request, 'base.html', {'content': 'Gestión de Servicios - Próximamente'})

@login_required
def employees_list(request):
    return render(request, 'base.html', {'content': 'Gestión de Empleados - Próximamente'})