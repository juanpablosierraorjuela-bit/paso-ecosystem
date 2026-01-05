from django.shortcuts import render
from apps.businesses.models import BusinessProfile
from django.utils import timezone

def marketplace_home(request):
    # Traemos todos los negocios del sistema
    businesses = BusinessProfile.objects.all()
    
    # Aquí podríamos agregar lógica de filtros por ciudad más adelante
    return render(request, 'marketplace/index.html', {'businesses': businesses})
