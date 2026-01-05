from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def owner_dashboard(request):
    return render(request, 'businesses/dashboard.html')
