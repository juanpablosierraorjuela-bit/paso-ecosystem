import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. CREAR LA VISTA (LOGIC)
# ==========================================
views_content = """
from django.shortcuts import render
from apps.businesses.models import Salon

def home(request):
    # Por ahora mostramos todos los salones (Fase 3 inicial)
    salons = Salon.objects.all()
    return render(request, 'marketplace/index.html', {'salons': salons})
"""

# ==========================================
# 2. ACTIVAR LA RUTA (URL)
# ==========================================
urls_content = """
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('salon/<int:pk>/', views.salon_detail, name='salon_detail'), # Pendiente siguiente paso
]
"""

# ==========================================
# 3. DISEÑAR LA VITRINA (TEMPLATE)
# ==========================================
html_content = """
{% extends 'base.html' %}

{% block content %}
<div class="bg-black text-white py-20 px-4">
    <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-4xl md:text-6xl font-serif mb-6 text-gold-500">
            Encuentra la Excelencia.
        </h1>
        <p class="text-gray-400 mb-8 text-lg">
            Los mejores expertos en belleza de Colombia, a un clic.
        </p>
        
        <div class="relative max-w-2xl mx-auto">
            <input type="text" 
                   placeholder="¿Qué buscas? Ej: 'Keratina', 'Barba Vikinga', 'Uñas Acrílicas'..." 
                   class="w-full py-4 px-8 rounded-full text-gray-900 bg-white focus:outline-none focus:ring-4 focus:ring-yellow-500 shadow-xl text-lg placeholder-gray-500">
            <button class="absolute right-2 top-2 bg-black text-white rounded-full p-2 px-6 hover:bg-gray-800 transition-colors mt-0.5">
                Buscar
            </button>
        </div>
        
        <div class="mt-8 flex justify-center space-x-4 text-sm text-gray-400">
            <span>Bogotá</span>
            <span>Medellín</span>
            <span>Cali</span>
            <span class="text-yellow-500 cursor-pointer">Ver todas</span>
        </div>
    </div>
</div>

<div class="container mx-auto px-4 py-16">
    <div class="flex justify-between items-center mb-8">
        <h2 class="text-2xl font-serif text-gray-900">Destacados cerca de ti</h2>
        <button class="text-sm font-bold underline">Filtrar por ubicación</button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        
        {% for salon in salons %}
        <div class="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all hover:-translate-y-1 border border-gray-100 group">
            <div class="relative h-48 bg-gray-200 flex items-center justify-center">
                <span class="absolute top-4 right-4 bg-green-400 text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm z-10">
                    ABIERTO
                </span>
                <span class="text-4xl font-serif text-gray-400">{{ salon.name|slice:":1" }}</span>
            </div>
            
            <div class="p-6">
                <h3 class="text-xl font-bold font-serif mb-1">{{ salon.name }}</h3>
                <p class="text-sm text-gray-500 mb-4">{{ salon.address }}, {{ salon.city }}</p>
                
                <div class="flex justify-between items-center mt-4">
                    <a href="#" class="text-black font-bold text-sm border-b-2 border-black hover:text-gray-600 hover:border-gray-600 transition-colors">
                        Ver Servicios
                    </a>
                    <div class="flex space-x-2">
                        <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 hover:bg-black hover:text-white transition-colors cursor-pointer">
                            📍
                        </div>
                        <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 hover:bg-pink-600 hover:text-white transition-colors cursor-pointer">
                            📸
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-span-3 text-center py-12">
            <p class="text-gray-400 text-lg">Aún no hay ecosistemas registrados.</p>
            <a href="{% url 'register_owner' %}" class="mt-4 inline-block bg-black text-white px-6 py-2 rounded-lg">¡Sé el primero!</a>
        </div>
        {% endfor %}

    </div>
</div>
{% endblock %}
"""

def run_fix():
    # 1. Crear views.py
    views_path = BASE_DIR / 'apps' / 'marketplace' / 'views.py'
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(views_content.strip())
    print("✅ apps/marketplace/views.py creado.")

    # 2. Actualizar urls.py
    urls_path = BASE_DIR / 'apps' / 'marketplace' / 'urls.py'
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content.strip())
    print("✅ apps/marketplace/urls.py actualizado.")

    # 3. Crear Template
    template_path = BASE_DIR / 'templates' / 'marketplace' / 'index.html'
    os.makedirs(template_path.parent, exist_ok=True)
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html_content.strip())
    print("✅ templates/marketplace/index.html creado.")

if __name__ == "__main__":
    run_fix()