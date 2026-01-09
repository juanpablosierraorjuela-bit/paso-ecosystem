import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. BASE.HTML (FAVICON + ESTILOS GLOBALES DE LUJO)
# ==========================================
html_base = """
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PASO Ecosistema | Belleza & Bienestar</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
    
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><circle cx=%2250%22 cy=%2250%22 r=%2250%22 fill=%22white%22/><text x=%2250%22 y=%2250%22 font-family=%22serif%22 font-size=%2260%22 fill=%22black%22 text-anchor=%22middle%22 dy=%22.35em%22 font-weight=%22bold%22>P</text></svg>">

    <style>
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Lato', sans-serif; }
        
        /* Fondo Premium General */
        body {
            background-color: #f8f9fa;
            background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
            background-size: 40px 40px;
        }
        
        /* Efecto Cristal (Glassmorphism) */
        .glass-panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Color Dorado Personalizado */
        .text-gold { color: #D4AF37; }
        .bg-gold { background-color: #D4AF37; }
        .border-gold { border-color: #D4AF37; }
        .hover-gold:hover { color: #AA8C2C; }
    </style>
</head>
<body class="font-sans flex flex-col min-h-screen text-gray-900 selection:bg-gold selection:text-white">

    <nav class="bg-black/95 text-white py-5 shadow-2xl sticky top-0 z-50 backdrop-blur-md">
        <div class="container mx-auto px-6 flex justify-between items-center">
            <a href="/" class="text-3xl font-serif font-bold text-white tracking-widest hover:text-gold transition duration-300 flex items-center gap-2">
                <span class="text-gold text-4xl">✦</span> PASO
            </a>

            <div class="flex items-center space-x-8 text-sm font-bold tracking-wide">
                <a href="{% url 'marketplace_home' %}" class="hover:text-gold transition duration-300 uppercase">Explorar</a>
                
                {% if user.is_authenticated %}
                    <span class="text-gray-400 hidden md:inline font-serif italic">Hola, {{ user.first_name }}</span>
                    
                    {% if user.role == 'OWNER' %}
                        <a href="{% url 'dashboard' %}" class="bg-white text-black px-6 py-2 rounded-full hover:bg-gold hover:text-white transition duration-300 shadow-lg">
                            MI PANEL
                        </a>
                    {% elif user.role == 'CLIENT' %}
                        <a href="{% url 'client_dashboard' %}" class="bg-white text-black px-6 py-2 rounded-full hover:bg-gold hover:text-white transition duration-300 shadow-lg">
                            MIS CITAS
                        </a>
                    {% elif user.role == 'EMPLOYEE' %}
                        <a href="{% url 'employee_dashboard' %}" class="bg-white text-black px-6 py-2 rounded-full hover:bg-gold hover:text-white transition duration-300 shadow-lg">
                            MI AGENDA
                        </a>
                    {% endif %}
                    
                    <form action="{% url 'logout' %}" method="post" class="inline">
                        {% csrf_token %}
                        <button type="submit" class="text-gray-400 hover:text-red-400 ml-4 transition text-xs uppercase">Salir</button>
                    </form>
                {% else %}
                    <a href="{% url 'landing_owners' %}" class="hidden md:inline text-gray-300 hover:text-white transition">Negocios</a>
                    <a href="{% url 'login' %}" class="bg-white text-black px-6 py-2 rounded-full hover:bg-gold hover:text-white transition duration-300 shadow-[0_0_15px_rgba(255,255,255,0.3)]">
                        ACCEDER
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>

    <main class="flex-grow">
        {% if messages %}
            <div class="max-w-4xl mx-auto mt-6 px-4 absolute top-20 left-0 right-0 z-40">
                {% for message in messages %}
                    <div class="p-4 rounded-xl shadow-2xl mb-2 text-white text-center font-bold glass-panel
                        {% if message.tags == 'success' %}bg-green-600/90{% elif message.tags == 'error' %}bg-red-600/90{% else %}bg-blue-600/90{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    <footer class="bg-black text-white py-12 mt-12 border-t border-gray-900">
        <div class="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
            <div class="mb-6 md:mb-0 text-center md:text-left">
                <p class="text-2xl font-serif font-bold text-white mb-2">PASO <span class="text-gold">.</span></p>
                <p class="text-sm text-gray-500 font-light tracking-wider">REDEFINIENDO EL ESTÁNDAR DE BELLEZA EN COLOMBIA.</p>
            </div>
            <div class="text-xs text-gray-600 font-mono">
                &copy; 2026 ECOSISTEMA PASO. TODOS LOS DERECHOS RESERVADOS.
            </div>
            <div class="flex space-x-6 mt-6 md:mt-0">
                {% if global_settings.instagram_url %}
                    <a href="{{ global_settings.instagram_url }}" target="_blank" class="text-gray-500 hover:text-gold transition transform hover:scale-110">
                        INSTAGRAM
                    </a>
                {% endif %}
            </div>
        </div>
    </footer>

</body>
</html>
"""

# ==========================================
# 2. HOME.HTML (CLIENTE LANDING - LUJO)
# ==========================================
html_home = """
{% extends 'base.html' %}

{% block content %}
<div class="relative overflow-hidden min-h-[90vh] flex items-center">
    <div class="absolute inset-0 z-0">
        <img src="https://images.unsplash.com/photo-1600948836101-f9ffda59d250?q=80&w=2036&auto=format&fit=crop" 
             class="w-full h-full object-cover" alt="Luxury Spa Background">
        <div class="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-transparent"></div>
    </div>

    <div class="relative z-10 container mx-auto px-6">
        <div class="max-w-3xl">
            <span class="text-gold uppercase tracking-[0.3em] text-sm font-bold mb-4 block animate-pulse">
                Bienvenido a la Excelencia
            </span>
            <h1 class="text-5xl md:text-7xl font-serif font-bold text-white mb-6 leading-tight">
                El Ecosistema para <br>
                <span class="italic text-gray-300">tu mejor versión.</span>
            </h1>
            <p class="text-xl text-gray-300 mb-10 font-light max-w-xl leading-relaxed">
                Desde spas exclusivos hasta los mejores estilistas de Colombia. Reserva tu experiencia con seguridad y sofisticación.
            </p>
            
            <div class="flex flex-col sm:flex-row gap-6">
                <a href="{% url 'marketplace_home' %}" class="group relative px-8 py-4 bg-white text-black font-bold rounded-full overflow-hidden shadow-[0_0_20px_rgba(255,255,255,0.4)] hover:shadow-[0_0_30px_rgba(212,175,55,0.6)] transition-all duration-300 text-center">
                    <span class="relative z-10 group-hover:text-gold transition">BUSCAR SERVICIOS</span>
                </a>
                
                <a href="{% url 'landing_owners' %}" class="px-8 py-4 border border-white/30 text-white font-bold rounded-full hover:bg-white/10 backdrop-blur-sm transition-all duration-300 text-center flex items-center justify-center gap-2">
                    <span>SOY EMPRESARIO</span>
                    <span class="text-gold">→</span>
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 3. LANDING_OWNERS.HTML (VENTAS DUEÑO - LUJO)
# ==========================================
html_landing_owners = """
{% extends 'base.html' %}

{% block content %}
<div class="bg-white">
    <div class="relative bg-black text-white py-32 px-6 overflow-hidden">
        <div class="absolute inset-0 opacity-40">
            <img src="https://images.unsplash.com/photo-1633681926022-84c23e8cb2d6?q=80&w=2070&auto=format&fit=crop" class="w-full h-full object-cover">
        </div>
        <div class="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black"></div>
        
        <div class="relative container mx-auto text-center max-w-4xl">
            <span class="border border-gold text-gold px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest mb-6 inline-block">
                Solo para Negocios Visionarios
            </span>
            <h1 class="text-5xl md:text-7xl font-serif font-bold mb-8 leading-none">
                Eleva tu Estándar. <br> Automatiza tu Éxito.
            </h1>
            <p class="text-2xl text-gray-300 mb-12 font-light">
                Spas, Salones, Barberías y Clínicas Estéticas. <br>
                La plataforma que gestiona tu agenda mientras tú cuidas a tus clientes.
            </p>
            <a href="{% url 'register_owner' %}" class="bg-gold text-black font-bold py-5 px-12 rounded-full hover:bg-white transition-all duration-500 shadow-2xl transform hover:-translate-y-1 text-lg">
                INICIAR REGISTRO
            </a>
            <p class="mt-6 text-sm text-gray-500 font-mono uppercase">Sin contratos forzosos • Activación Inmediata</p>
        </div>
    </div>

    <div class="py-24 bg-gray-50">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-12">
                <div class="bg-white p-10 rounded-3xl shadow-xl border border-gray-100 hover:border-gold transition duration-500 group">
                    <div class="text-5xl mb-6 grayscale group-hover:grayscale-0 transition">🕰️</div>
                    <h3 class="text-2xl font-serif font-bold mb-4">Agenda Caótica</h3>
                    <p class="text-gray-600 leading-relaxed">
                        ¿Sigues usando papel y lápiz? Los tachones y las citas dobles son cosa del pasado. Digitaliza tu recepción.
                    </p>
                </div>
                <div class="bg-white p-10 rounded-3xl shadow-xl border border-gray-100 hover:border-gold transition duration-500 group">
                    <div class="text-5xl mb-6 grayscale group-hover:grayscale-0 transition">📱</div>
                    <h3 class="text-2xl font-serif font-bold mb-4">WhatsApp Infinito</h3>
                    <p class="text-gray-600 leading-relaxed">
                        Deja de responder "¿Qué precio tiene?" cien veces al día. Tu menú de servicios vende por ti 24/7.
                    </p>
                </div>
                <div class="bg-white p-10 rounded-3xl shadow-xl border border-gray-100 hover:border-gold transition duration-500 group">
                    <div class="text-5xl mb-6 grayscale group-hover:grayscale-0 transition">👻</div>
                    <h3 class="text-2xl font-serif font-bold mb-4">No-Shows</h3>
                    <p class="text-gray-600 leading-relaxed">
                        El sistema PASO protege tu tiempo. Sin abono confirmado, la cita no bloquea tu agenda. Cero pérdidas.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <div class="bg-black text-white py-24 text-center border-t border-gray-900">
        <div class="container mx-auto px-6">
            <h2 class="text-4xl font-serif font-bold mb-8 text-gold">Tu negocio merece este nivel.</h2>
            <div class="flex flex-col md:flex-row justify-center items-center gap-6">
                <a href="{% url 'register_owner' %}" class="bg-white text-black font-bold py-4 px-10 rounded-full hover:bg-gray-200 transition shadow-lg w-full md:w-auto">
                    Crear Cuenta Empresarial
                </a>
                <a href="{% url 'marketplace_home' %}" class="text-gray-400 border-b border-transparent hover:border-gray-400 pb-1 transition">
                    Explorar Marketplace
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 4. MARKETPLACE INDEX.HTML (BUSCADOR LUJO)
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

<div class="container mx-auto px-6 py-16 -mt-20 relative z-20">
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

# ==========================================
# 5. REGISTRO & LOGIN (GLASSMORPHISM)
# ==========================================
html_login = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-20 px-4 relative overflow-hidden bg-black">
    <div class="absolute inset-0 opacity-40">
        <img src="https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?q=80&w=2070&auto=format&fit=crop" class="w-full h-full object-cover">
    </div>
    
    <div class="glass-panel max-w-md w-full p-10 rounded-3xl shadow-2xl relative z-10 border border-white/10">
        <div class="text-center mb-10">
            <h2 class="text-3xl font-serif font-bold text-gray-900">Bienvenido</h2>
            <p class="mt-2 text-sm text-gray-500">Accede a tu panel de control</p>
        </div>

        <form class="space-y-6" method="post" action="{% url 'login' %}">
            {% csrf_token %}
            {% if form.errors %}
                <div class="bg-red-50 text-red-600 p-3 rounded text-sm text-center mb-4">Credenciales inválidas.</div>
            {% endif %}

            <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Usuario</label>
                <input type="text" name="username" required class="block w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:outline-none transition">
            </div>

            <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Contraseña</label>
                <input type="password" name="password" required class="block w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:outline-none transition">
            </div>

            <button type="submit" class="w-full py-4 bg-black text-white font-bold rounded-xl hover:bg-gold transition duration-300 shadow-lg mt-4">
                INGRESAR
            </button>

            <div class="text-center mt-6 text-sm">
                <a href="{% url 'register_owner' %}" class="text-gray-500 hover:text-black transition">¿Nuevo aquí? <span class="font-bold underline">Crear cuenta</span></a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""

html_register = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-20 px-4 relative overflow-hidden bg-gray-50">
    <div class="absolute top-0 left-0 w-full h-96 bg-black z-0"></div>
    
    <div class="max-w-3xl w-full bg-white p-10 md:p-14 rounded-3xl shadow-2xl relative z-10 border border-gray-100">
        <div class="text-center mb-10">
            <span class="text-gold font-bold tracking-widest text-xs uppercase">Registro Empresarial</span>
            <h2 class="mt-2 text-4xl font-serif font-bold text-gray-900">Crea tu Ecosistema</h2>
        </div>
        
        <form class="space-y-10" method="POST">
            {% csrf_token %}
            
            {% if form.errors %}
                <div class="bg-red-50 p-4 rounded-lg text-red-600 text-sm mb-6">
                    Por favor revisa los campos marcados.
                </div>
            {% endif %}

            <div>
                <h3 class="text-xl font-bold text-black border-b border-gray-100 pb-4 mb-6 flex items-center gap-2">
                    <span class="bg-black text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span> 
                    Datos del Propietario
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Nombre</label>{{ form.first_name }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Apellido</label>{{ form.last_name }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">WhatsApp</label>{{ form.phone }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Ciudad</label>{{ form.city }}</div>
                </div>
            </div>

            <div>
                <h3 class="text-xl font-bold text-black border-b border-gray-100 pb-4 mb-6 flex items-center gap-2">
                    <span class="bg-black text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">2</span> 
                    Datos del Negocio
                </h3>
                <div class="space-y-6">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Nombre del Establecimiento</label>{{ form.salon_name }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Dirección Física</label>{{ form.salon_address }}</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Instagram (Opcional)</label>{{ form.instagram_url }}</div>
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Google Maps (Opcional)</label>{{ form.google_maps_url }}</div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-50 p-8 rounded-2xl border border-gray-200">
                <h3 class="text-xl font-bold text-black border-b border-gray-200 pb-4 mb-6 flex items-center gap-2">
                    <span class="bg-black text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">3</span> 
                    Credenciales de Acceso
                </h3>
                <div class="grid grid-cols-1 gap-6">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Usuario</label>{{ form.username }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Email</label>{{ form.email }}</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Contraseña</label>{{ form.password1 }}</div>
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Confirmar</label>{{ form.password2 }}</div>
                    </div>
                </div>
            </div>

            <button type="submit" class="w-full py-5 bg-gold text-black font-bold rounded-xl hover:bg-black hover:text-white transition duration-500 shadow-xl text-lg tracking-widest uppercase">
                Finalizar Registro
            </button>
        </form>
    </div>
</div>
{% endblock %}
"""

def apply_luxury_design():
    print("💎 APLICANDO DISEÑO PREMIUM (GOLD & GLASS)...")

    # 1. Base (Favicon + Styles)
    with open(BASE_DIR / 'templates' / 'base.html', 'w', encoding='utf-8') as f:
        f.write(html_base.strip())
    print("✅ Base actualizada: Favicon P y estilos globales.")

    # 2. Home (Landing Cliente)
    with open(BASE_DIR / 'templates' / 'home.html', 'w', encoding='utf-8') as f:
        f.write(html_home.strip())
    print("✅ Home actualizado: Imágenes de Spa y copy inclusivo.")

    # 3. Landing Owners (Ventas)
    with open(BASE_DIR / 'templates' / 'landing_owners.html', 'w', encoding='utf-8') as f:
        f.write(html_landing_owners.strip())
    print("✅ Landing Owners actualizada: Diseño high-end.")

    # 4. Marketplace (Buscador)
    with open(BASE_DIR / 'templates' / 'marketplace' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_marketplace.strip())
    print("✅ Marketplace actualizado: Buscador flotante y tarjetas premium.")

    # 5. Login
    with open(BASE_DIR / 'templates' / 'registration' / 'login.html', 'w', encoding='utf-8') as f:
        f.write(html_login.strip())
    print("✅ Login actualizado: Glassmorphism.")

    # 6. Registro
    with open(BASE_DIR / 'templates' / 'registration' / 'register_owner.html', 'w', encoding='utf-8') as f:
        f.write(html_register.strip())
    print("✅ Registro actualizado: Formulario limpio y elegante.")

if __name__ == "__main__":
    apply_luxury_design()