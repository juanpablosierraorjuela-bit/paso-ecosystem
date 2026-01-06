from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BusinessProfile, Service, OperatingHour
from .forms import ServiceForm, OperatingHourForm

@login_required
def services_list(request):
    # Verificar que sea dueño
    if request.user.role != 'OWNER':
        return redirect('home')
    
    business = request.user.business_profile
    services = business.services.all()
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.business = business
            service.save()
            messages.success(request, '✅ Servicio agregado exitosamente.')
            return redirect('businesses:services')
    else:
        form = ServiceForm()

    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def schedule_list(request):
    if request.user.role != 'OWNER':
        return redirect('home')
        
    business = request.user.business_profile
    hours = business.operating_hours.all().order_by('day_of_week')
    
    if request.method == 'POST':
        form = OperatingHourForm(request.POST)
        if form.is_valid():
            # Evitar duplicados de día
            day = form.cleaned_data['day_of_week']
            OperatingHour.objects.filter(business=business, day_of_week=day).delete()
            
            hour = form.save(commit=False)
            hour.business = business
            hour.save()
            messages.success(request, '✅ Horario actualizado.')
            return redirect('businesses:schedule')
    else:
        form = OperatingHourForm()

    return render(request, 'businesses/schedule.html', {'hours': hours, 'form': form})
