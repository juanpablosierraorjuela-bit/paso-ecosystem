import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# DISEÑO DE LA PANTALLA DE LOGIN
# ==========================================
login_html = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white p-10 rounded-2xl shadow-xl border border-gray-100">
        
        <div class="text-center mb-10">
            <h2 class="text-3xl font-serif font-bold text-gray-900">Bienvenido de nuevo</h2>
            <p class="mt-2 text-sm text-gray-500">Ingresa a tu ecosistema PASO</p>
        </div>

        <form class="space-y-6" method="post" action="{% url 'login' %}">
            {% csrf_token %}
            
            {% if form.errors %}
                <div class="bg-red-50 text-red-600 p-3 rounded text-sm text-center mb-4">
                    Usuario o contraseña incorrectos.
                </div>
            {% endif %}

            <div>
                <label for="id_username" class="block text-sm font-medium text-gray-700">Usuario</label>
                <div class="mt-1">
                    <input type="text" name="username" autofocus required id="id_username" 
                        class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm">
                </div>
            </div>

            <div>
                <label for="id_password" class="block text-sm font-medium text-gray-700">Contraseña</label>
                <div class="mt-1">
                    <input type="password" name="password" required id="id_password" 
                        class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm">
                </div>
            </div>

            <div>
                <button type="submit" class="w-full flex justify-center py-4 px-4 border border-transparent text-sm font-bold rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
                    ENTRAR AL SISTEMA
                </button>
            </div>

            <div class="flex items-center justify-between mt-4">
                <div class="text-sm">
                    <a href="{% url 'register_owner' %}" class="font-medium text-gray-600 hover:text-black">
                        ¿No tienes cuenta? <span class="underline">Regístrate</span>
                    </a>
                </div>
                <div class="text-sm">
                    <a href="#" class="font-medium text-gray-400 hover:text-gray-500">
                        ¿Olvidaste tu clave?
                    </a>
                </div>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# EJECUTAR CREACIÓN
# ==========================================
def fix_login_template():
    # Asegurar que la carpeta existe
    target_dir = BASE_DIR / 'templates' / 'registration'
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = target_dir / 'login.html'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(login_html.strip())
    
    print(f"✅ Creado exitosamente: {file_path}")

if __name__ == "__main__":
    fix_login_template()
    print("🚀 Login reparado. Ahora sube los cambios.")