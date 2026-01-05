from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import OwnerRegistrationForm
from django.urls import reverse_lazy
from .models import User
from apps.businesses.models import BusinessProfile, OperatingHour

def pain_landing(request):
    return render(request, 'landing/pain_points.html')

class OwnerRegisterView(CreateView):
    model = User
    form_class = OwnerRegistrationForm
    template_name = 'registration/register_owner.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.OWNER
        user.save()
        
        # BLINDAJE: Crear perfil inmediatamente
        if not hasattr(user, 'business_profile'):
            biz_name = form.cleaned_data.get('business_name', f"Negocio de {user.first_name}")
            address = form.cleaned_data.get('address', "Dirección pendiente")
            
            profile = BusinessProfile.objects.create(
                owner=user,
                business_name=biz_name,
                address=address
            )
            # Crear horarios
            for day_code, _ in OperatingHour.DAYS:
                OperatingHour.objects.create(business=profile, day_of_week=day_code, opening_time="09:00", closing_time="19:00", is_closed=(day_code==6))
                
        return super().form_valid(form)

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == User.Role.OWNER:
        return redirect('businesses:dashboard')
    elif user.role == User.Role.EMPLOYEE:
        return redirect('booking:employee_dashboard')
    elif user.role == User.Role.CLIENT:
        return redirect('booking:client_dashboard')
    elif user.is_staff:
        return redirect('/admin/')
    return redirect('home')
