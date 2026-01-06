
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Salon
from apps.core.models import GlobalSettings

@login_required
def owner_dashboard(request):
    # Seguridad: Solo dueños
    if request.user.role != 'OWNER':
        return redirect('home')
        
    user = request.user
    salon = getattr(user, 'salon', None)
    settings = GlobalSettings.objects.first()
    
    # 1. Lógica del "Reaper" (Tiempo Restante)
    hours_since = user.hours_since_registration()
    hours_remaining = 24 - hours_since
    is_expired = hours_remaining <= 0 and not user.is_verified_payment
    
    # 2. Mensaje de WhatsApp para Activación
    wa_message = f"Hola PASO, soy {user.first_name} (ID: {user.id}). Quiero activar mi ecosistema para {salon.name if salon else 'mi negocio'}."
    wa_link = f"https://wa.me/{settings.support_whatsapp}?text={wa_message}" if settings else "#"

    context = {
        'salon': salon,
        'hours_remaining': max(0, int(hours_remaining)),
        'hours_percent': (max(0, hours_remaining) / 24) * 100,
        'is_verified': user.is_verified_payment,
        'is_expired': is_expired,
        'wa_link': wa_link
    }
    return render(request, 'businesses/dashboard.html', context)
