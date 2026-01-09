import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. MARKETPLACE INDEX.HTML (AJUSTE DE MARGEN)
# ==========================================
html_marketplace = """
{% extends 'base.html' %}

{% block content %}
<div class="bg-black text-white pt-24 pb-32 px-6 relative overflow-hidden">
    <div class="absolute top-0 right-0 w-64 h-64 bg-gold opacity-10 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2"></div>
    <div class="max-w-5xl mx-auto text-center relative z-10">
        <h1 class="text-4xl md:text-5xl font-serif font-bold mb-4 text-white">
            Descubre Expertos
        </h1>
        <p class="text-gray-400 mb-10 font-light">Estética, Barbería, Spa y Bienestar.</p>
        
        <div class="bg-white/10 backdrop-blur-md p-2 rounded-2xl border border-white/20 shadow-2xl">
            <form method="GET" action="{% url 'marketplace_home' %}" class="flex flex-col md:flex-row gap-2">
                
                <div class="flex-grow relative">
                    <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    </div>
                    <input type="text" name="q" value="{{ current_query }}" placeholder="Ej: Tierra de Reinas, Corte..." 
                           class="w-full pl-12 pr-4 py-4 rounded-xl bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gold border-none">
                </div>

                <div class="md:w-1/3">
                    <select name="city" onchange="this.form.submit()" 
                            class="w-full px-4 py-4 rounded-xl bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gold border-none cursor-pointer">
                        <option value="">Todas las Ciudades</option>
                        {% for city in cities %}
                            <option value="{{ city }}" {% if city == current_city %}selected{% endif %}>
                                {{ city }}
                            </option>
                        {% endfor %}
                    </select>
                </div>

                <button type="submit" class="bg-gold text-black font-bold py-4 px-8 rounded-xl hover:bg-white transition duration-300">
                    BUSCAR
                </button>
            </form>
        </div>
    </div>
</div>

<div class="container mx-auto px-6 py-12 relative z-20">
    <div class="flex items-center justify-between mb-8">
        <h2 class="text-2xl font-serif font-bold text-gray-900">
            Resultados Destacados
            {% if current_city %} <span class="text-gold">en {{ current_city }}</span> {% endif %}
        </h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {% for salon in salons %}
        <div class="bg-white rounded-2xl overflow-hidden hover:shadow-2xl transition-all duration-500 border border-gray-100 group flex flex-col h-full">
            
            <div class="h-56 bg-gray-100 relative overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10"></div>
                
                {% if salon.is_open_now %}
                    <span class="absolute top-4 right-4 z-20 bg-white/90 backdrop-blur text-green-700 text-[10px] font-bold px-3 py-1 rounded-full shadow-sm uppercase tracking-wider">
                        Disponible
                    </span>
                {% else %}
                    <span class="absolute top-4 right-4 z-20 bg-black/50 backdrop-blur text-white text-[10px] font-bold px-3 py-1 rounded-full shadow-sm uppercase tracking-wider">
                        Cerrado
                    </span>
                {% endif %}
                
                <div class="w-full h-full flex items-center justify-center bg-gray-200 group-hover:scale-105 transition duration-700">
                    <span class="text-6xl font-serif text-gray-400 font-bold opacity-30">{{ salon.name|slice:":1" }}</span>
                </div>
            </div>
            
            <div class="p-8 flex-grow flex flex-col">
                <h3 class="text-2xl font-serif font-bold mb-2 group-hover:text-gold transition">{{ salon.name }}</h3>
                <p class="text-sm text-gray-500 mb-6 flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    {{ salon.city }}
                </p>
                
                <div class="mt-auto pt-6 border-t border-gray-100 flex justify-between items-center">
                    <a href="{% url 'salon_detail' salon.pk %}" class="text-black font-bold text-sm border-b-2 border-black hover:border-gold hover:text-gold transition pb-1">
                        Reservar Cita
                    </a>
                    
                    <div class="flex space-x-3 opacity-60 group-hover:opacity-100 transition">
                        {% if salon.owner.phone %}
                        <a href="https://wa.me/57{{ salon.owner.phone }}" target="_blank" class="hover:text-green-600 transition" title="WhatsApp">💬</a>
                        {% endif %}
                        {% if salon.instagram_url %}
                        <a href="{{ salon.instagram_url }}" target="_blank" class="hover:text-pink-600 transition" title="Instagram">📸</a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-span-3 py-20 text-center">
            <p class="text-gray-400 font-serif text-xl italic mb-4">"La belleza está en todas partes, pero no aquí..."</p>
            <p class="text-gray-500 text-sm">No encontramos resultados para tu búsqueda.</p>
            <a href="{% url 'marketplace_home' %}" class="mt-6 inline-block text-gold underline font-bold">Ver todo el catálogo</a>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

def fix_title_margin():
    print("🔧 AJUSTANDO MARGEN DEL TÍTULO EN MARKETPLACE...")
    with open(BASE_DIR / 'templates' / 'marketplace' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_marketplace.strip())
    print("✅ templates/marketplace/index.html: Margen corregido.")

if __name__ == "__main__":
    fix_title_margin()