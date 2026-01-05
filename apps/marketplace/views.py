from django.shortcuts import render, get_object_or_404
from apps.businesses.models import BusinessProfile

def marketplace_home(request):
    businesses = BusinessProfile.objects.all()
    return render(request, 'marketplace/index.html', {'businesses': businesses})

def business_detail(request, business_id):
    # Buscamos el negocio
    business = get_object_or_404(BusinessProfile, id=business_id)
    
    # Traemos sus servicios activos
    services = business.services.filter(is_active=True)
    
    # Traemos sus empleados (staff)
    employees = business.staff.filter(is_active=True)
    
    return render(request, 'marketplace/business_detail.html', {
        'business': business,
        'services': services,
        'employees': employees
    })
