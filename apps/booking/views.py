from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def employee_dashboard(request):
    return render(request, 'booking/employee_dashboard.html')

@login_required
def client_dashboard(request):
    return render(request, 'booking/client_dashboard.html')
