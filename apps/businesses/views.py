from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def owner_dashboard(request):
    # Lógica del temporizador y validación
    return render(request, 'businesses/dashboard.html')