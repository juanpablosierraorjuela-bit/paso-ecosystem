from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from apps.businesses.models import BusinessProfile

def marketplace_home(request):
    query = request.GET.get('q')
    businesses = BusinessProfile.objects.all()
    
    if query:
        # LÓGICA DE BÚSQUEDA SEMÁNTICA
        # Busca en el nombre del negocio O en la descripción de sus servicios
        businesses = businesses.filter(
            Q(business_name__icontains=query) | 
            Q(description__icontains=query) |
            Q(services__name__icontains=query) |
            Q(services__description__icontains=query)
        ).distinct()

    return render(request, 'marketplace/index.html', {'businesses': businesses, 'query': query})

def business_detail(request, business_id):
    business = get_object_or_404(BusinessProfile, id=business_id)
    services = business.services.filter(is_active=True)
    employees = business.staff.filter(is_active=True)
    return render(request, 'marketplace/business_detail.html', {
        'business': business, 'services': services, 'employees': employees
    })
