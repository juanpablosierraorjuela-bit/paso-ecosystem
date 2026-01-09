from django.shortcuts import render
from apps.businesses.models import Salon

def home(request):
    # Por ahora mostramos todos los salones (Fase 3 inicial)
    salons = Salon.objects.all()
    return render(request, 'marketplace/index.html', {'salons': salons})