from django.shortcuts import render, get_object_or_404, redirect
from .models import Salon, Service
from math import radians, cos, sin, asin, sqrt # <--- IMPORTANTE: Agrega esto al inicio

# Función para calcular distancia (Haversine)
def haversine(lon1, lat1, lon2, lat2):
    """
    Calcula la distancia en kilómetros entre dos puntos geográficos
    """
    # Convertir grados decimales a radianes
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Fórmula de haversine
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radio de la Tierra en km
    return c * r

def home(request):
    salons = Salon.objects.all()
    
    # Obtener lista de ciudades únicas para el filtro
    all_cities = Salon.objects.values_list('city', flat=True).distinct()

    # 1. Filtro por Ciudad (si se selecciona en el menú)
    city_param = request.GET.get('city')
    if city_param:
        salons = salons.filter(city=city_param)

    # 2. Filtro por Geolocalización (600 metros)
    lat_param = request.GET.get('lat')
    lon_param = request.GET.get('lon')
    nearby_search = False # Bandera para saber si estamos buscando por cercanía

    if lat_param and lon_param:
        nearby_search = True
        try:
            user_lat = float(lat_param)
            user_lon = float(lon_param)
            
            nearby_salons = []
            for salon in salons:
                # Solo calcular si el salón tiene coordenadas guardadas
                if salon.latitude and salon.longitude:
                    # Ojo: Asegúrate de que en tu modelo latitude/longitude sean FloatField o DecimalField
                    # Si son CharField, conviértelos: float(salon.latitude)
                    dist = haversine(user_lon, user_lat, float(salon.longitude), float(salon.latitude))
                    
                    # 0.6 km = 600 metros
                    if dist <= 0.6:
                        nearby_salons.append(salon)
            
            salons = nearby_salons # Reemplazamos la lista con los cercanos
            
        except (ValueError, TypeError):
            pass # Si las coordenadas fallan, mostramos todo por defecto

    context = {
        'salons': salons,
        'all_cities': all_cities,
        'nearby_search': nearby_search
    }
    return render(request, 'home.html', context)

# ... (El resto de tus vistas: salon_detail, booking, etc. déjalas igual)