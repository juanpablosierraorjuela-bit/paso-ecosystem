import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# CONTENIDO CORREGIDO (CLIENT DASHBOARD)
# ==========================================
# Quitamos '|floatform:0' en la línea 31
html_client_dash_fixed = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-serif font-bold mb-2">Mis Citas</h1>
    <p class="text-gray-500 mb-8">Gestiona tus reservas y pagos pendientes.</p>

    <div class="space-y-6">
        {% for app in appointments %}
        <div class="bg-white rounded-xl shadow border-l-4 {% if app.status == 'PENDING' %}border-yellow-400{% else %}border-green-500{% endif %} p-6 flex flex-col md:flex-row justify-between items-start md:items-center">
            
            <div class="mb-4 md:mb-0">
                <div class="flex items-center space-x-2 mb-1">
                    <h3 class="text-xl font-bold">{{ app.service.name }}</h3>
                    {% if app.status == 'PENDING' %}
                        <span class="bg-yellow-100 text-yellow-800 text-xs font-bold px-2 py-0.5 rounded">PENDIENTE PAGO</span>
                    {% else %}
                        <span class="bg-green-100 text-green-800 text-xs font-bold px-2 py-0.5 rounded">CONFIRMADA</span>
                    {% endif %}
                </div>
                <p class="text-gray-600">{{ app.salon.name }} &bull; con {{ app.employee.first_name }}</p>
                <p class="text-sm font-mono mt-1 text-gray-500">📅 {{ app.date_time|date:"D d M, Y - h:i A" }}</p>
            </div>

            <div class="w-full md:w-auto text-right">
                {% if app.status == 'PENDING' %}
                    <p class="text-xs text-red-500 font-bold mb-2">
                        Tiempo para pagar: <span id="timer-{{ app.id }}">--:--</span>
                    </p>
                    <a href="{{ app.wa_link }}" target="_blank" class="block w-full md:inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-700 transition shadow-lg flex items-center justify-center">
                        <span class="mr-2">📱</span> Enviar Abono (${{ app.deposit_amount }})
                    </a>
                    
                    <script>
                        (function() {
                            let seconds = {{ app.seconds_left }};
                            const timerEl = document.getElementById('timer-{{ app.id }}');
                            
                            const interval = setInterval(() => {
                                if (seconds <= 0) {
                                    clearInterval(interval);
                                    timerEl.innerText = "EXPIRADO";
                                    return;
                                }
                                let m = Math.floor(seconds / 60);
                                let s = seconds % 60;
                                timerEl.innerText = `${m}:${s < 10 ? '0'+s : s}`;
                                seconds--;
                            }, 1000);
                        })();
                    </script>
                {% else %}
                    <button class="text-gray-400 text-sm border border-gray-200 px-4 py-2 rounded cursor-not-allowed">
                        Comprobante Enviado
                    </button>
                {% endif %}
            </div>

        </div>
        {% empty %}
        <div class="text-center py-12">
            <p class="text-gray-400">No tienes citas agendadas.</p>
            <a href="{% url 'marketplace_home' %}" class="mt-4 inline-block text-black underline font-bold">Ir al Marketplace</a>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

def apply_fix():
    print("🚑 ARREGLANDO TEMPLATE CLIENT DASHBOARD...")
    # Asegurar que el directorio existe
    os.makedirs(BASE_DIR / 'templates' / 'core', exist_ok=True)
    
    with open(BASE_DIR / 'templates' / 'core' / 'client_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_client_dash_fixed.strip())
    print("✅ Template reparado (floatform eliminado).")

if __name__ == "__main__":
    apply_fix()
    