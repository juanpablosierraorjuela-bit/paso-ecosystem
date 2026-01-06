from django.shortcuts import render, redirect
from django.contrib.auth import login
from apps.businesses.forms import OwnerRegistrationForm

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.user.is_authenticated:
        return redirect('businesses:dashboard')
        
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login
            return redirect('businesses:dashboard')
    else:
        form = OwnerRegistrationForm()
        
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    # Placeholder login logic (Django auth views should be used in prod urls)
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='registration/login.html')(request)


from apps.marketplace.models import Appointment

@login_required
def client_dashboard(request):
    if request.user.role != 'CLIENT': return redirect('home')
    appointments = Appointment.objects.filter(client=request.user).order_by('-date_time')
    return render(request, 'core/client_dashboard.html', {'appointments': appointments})

@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE': return redirect('home')
    # Empleado ve sus citas asignadas
    appointments = Appointment.objects.filter(employee=request.user, status='VERIFIED').order_by('date_time')
    return render(request, 'businesses/employee_dashboard.html', {'appointments': appointments})