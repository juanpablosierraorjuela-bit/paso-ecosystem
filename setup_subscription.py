import os

# CONFIGURACIÓN DE RUTAS CORREGIDA
# Usamos '.' porque ya estás dentro de la carpeta del proyecto
BASE_DIR = '.' 
APPS_DIR = os.path.join(BASE_DIR, 'apps')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

print(f"📂 Trabajando en el directorio actual: {os.getcwd()}")

# 1. MODIFICAR EL MODELO (models.py)
# ------------------------------------------------------------------
models_path = os.path.join(APPS_DIR, 'businesses', 'models.py')
print(f"🔧 Buscando archivo en: {models_path}...")

try:
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Agregamos los campos si no existen
    if 'is_active_subscription' not in content:
        anchor = 'is_open_manually = models.BooleanField("Abierto Manualmente", default=True)'
        new_fields = """
    is_open_manually = models.BooleanField("Abierto Manualmente", default=True)

    # --- CAMPOS DE SUSCRIPCIÓN (Ecosistema PASO) ---
    is_active_subscription = models.BooleanField("Suscripción Activa", default=False)
    subscription_end_date = models.DateField("Fecha Corte", null=True, blank=True)
    """
        # Reemplazo simple
        if anchor in content:
            content = content.replace(anchor, new_fields)
            with open(models_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   ✅ Campos agregados al modelo BusinessProfile.")
        else:
            print("   ⚠️ No encontré la línea de referencia en models.py. Verifica el archivo manualmente.")
    else:
        print("   ⚠️ Los campos ya existían en models.py.")

except FileNotFoundError:
    print(f"   ❌ ERROR CRÍTICO: No se encontró {models_path}")
    exit()


# 2. MODIFICAR LA VISTA DEL MARKETPLACE (views.py)
# ------------------------------------------------------------------
views_path = os.path.join(APPS_DIR, 'marketplace', 'views.py')
print(f"🔧 Modificando {views_path}...")

try:
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Cambiamos el query para filtrar solo activos
    old_query = 'businesses = BusinessProfile.objects.all()'
    new_query = 'businesses = BusinessProfile.objects.filter(is_active_subscription=True)'

    if old_query in content:
        content = content.replace(old_query, new_query)
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ Filtro de seguridad aplicado al Marketplace.")
    else:
        print("   ⚠️ El filtro ya estaba aplicado o no se encontró la línea exacta.")
except FileNotFoundError:
    print(f"   ❌ No se encontró {views_path}")


# 3. MODIFICAR EL TEMPLATE DE CONFIGURACIÓN (settings.html)
# ------------------------------------------------------------------
settings_path = os.path.join(TEMPLATES_DIR, 'businesses', 'settings.html')
print(f"🔧 Modificando {settings_path}...")

try:
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tarjeta de Suscripción UI
    subscription_card = """
    <div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #d4af37; height: fit-content;">
        <h3 style="margin-bottom: 20px; color: #d4af37;">💳 Mi Suscripción PASO</h3>
        
        <div style="margin-bottom: 20px;">
            <p style="color: #ccc; margin-bottom: 5px;">Plan Actual:</p>
            <strong style="font-size: 1.2rem; color: white;">Socio Ecosystem Pro</strong>
        </div>

        <div style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <p style="color: #ccc; margin-bottom: 5px;">Estado:</p>
                {% if request.user.business_profile.is_active_subscription %}
                    <span style="color: #4cd137; background: rgba(76, 209, 55, 0.1); padding: 5px 10px; border-radius: 5px;">● Activo</span>
                {% else %}
                    <span style="color: #e84118; background: rgba(232, 65, 24, 0.1); padding: 5px 10px; border-radius: 5px;">● Suspendido</span>
                {% endif %}
            </div>
            <div style="text-align: right;">
                <p style="color: #ccc; margin-bottom: 5px;">Corte:</p>
                <span style="color: white;">{{ request.user.business_profile.subscription_end_date|default:"--/--/--" }}</span>
            </div>
        </div>

        <hr style="border-color: #333; margin: 20px 0;">

        <div style="text-align: center;">
            <p style="color: #888; font-size: 0.9rem; margin-bottom: 15px;">Mensualidad: <strong>$50.000 COP</strong></p>
            
            <a href="https://wa.me/573000000000?text=Hola%20PASO,%20soy%20el%20negocio%20{{ request.user.business_profile.business_name }}%20(ID:%20{{ request.user.business_profile.id }}).%20Quiero%20pagar%20mi%20suscripcion." 
               target="_blank" 
               style="background: #25D366; color: white; text-decoration: none; padding: 12px 20px; border-radius: 5px; display: block; font-weight: bold;">
               🟢 Pagar vía WhatsApp
            </a>
            <p style="color: #555; font-size: 0.8rem; margin-top: 10px;">
                Envía tu comprobante para activar inmediatemente.
            </p>
        </div>
    </div>
    <div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #333; height: fit-content;">
    """

    if 'Mi Suscripción PASO' not in content:
        # Insertamos antes de la tarjeta de "Pagos y Abonos"
        # Usamos una parte única de esa línea para el reemplazo
        anchor_part = '<div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #333; height: fit-content;">'
        
        # Encontramos la primera ocurrencia (que debería ser la columna derecha original)
        if anchor_part in content:
             content = content.replace(anchor_part, subscription_card, 1)
             with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(content)
             print("   ✅ UI de Suscripción agregada a settings.html.")
        else:
             print("   ⚠️ No encontré el bloque 'Pagos y Abonos' para insertar antes.")
    else:
        print("   ⚠️ La tarjeta de suscripción ya existía.")

except FileNotFoundError:
    print(f"   ❌ No se encontró {settings_path}")


# 4. INSTALAR EL KILL SWITCH (base_dashboard.html)
# ------------------------------------------------------------------
base_dash_path = os.path.join(TEMPLATES_DIR, 'businesses', 'base_dashboard.html')
print(f"🔧 Modificando {base_dash_path}...")

try:
    with open(base_dash_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Lógica de bloqueo
    kill_switch_logic = """
    <main style="flex: 1; padding: 40px; margin-left: 250px; background: #000; color: white; position: relative;">
        
        {% if request.user.business_profile and not request.user.business_profile.is_active_subscription and request.resolver_match.url_name != 'settings' %}
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
            <h1 style="font-size: 3rem; margin-bottom: 20px;">⚠️</h1>
            <h2 style="color: white; margin-bottom: 10px;">Cuenta Suspendida Temporalmente</h2>
            <p style="color: #888; max-width: 500px; margin-bottom: 30px;">
                Tu mensualidad de <strong>$50.000 COP</strong> está pendiente. 
                Para reactivar tu agenda y visibilidad en la App, por favor regulariza tu pago.
            </p>
            <a href="{% url 'businesses:settings' %}" style="background: #d4af37; color: black; padding: 15px 30px; text-decoration: none; font-weight: bold; border-radius: 50px;">
                Ir a Pagar Ahora ➔
            </a>
        </div>
        {% endif %}

        {% block dashboard_content %}{% endblock %}
    </main>
    """

    # Reemplazamos el bloque main original
    original_main = """    <main style="flex: 1; padding: 40px; margin-left: 250px; background: #000; color: white;">
        {% block dashboard_content %}{% endblock %}
    </main>"""

    if 'KILL SWITCH OVERLAY' not in content:
        # Intentamos reemplazar normalizando espacios si es necesario (replace simple)
        if original_main in content:
            content = content.replace(original_main, kill_switch_logic)
            with open(base_dash_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   ✅ Kill Switch (Bloqueo de morosos) instalado en el Dashboard.")
        else:
            print("   ⚠️ No encontré el bloque <main> exacto para reemplazar. Verifica base_dashboard.html.")
    else:
        print("   ⚠️ El Kill Switch ya estaba instalado.")

except FileNotFoundError:
    print(f"   ❌ No se encontró {base_dash_path}")


# 5. CREAR EL MANAGEMENT COMMAND (desactivar_morosos.py)
# ------------------------------------------------------------------
cmd_dir = os.path.join(APPS_DIR, 'businesses', 'management', 'commands')
os.makedirs(cmd_dir, exist_ok=True)
# Asegurar __init__.py en management y commands
open(os.path.join(APPS_DIR, 'businesses', 'management', '__init__.py'), 'a').close()
open(os.path.join(cmd_dir, '__init__.py'), 'a').close()

cmd_file_path = os.path.join(cmd_dir, 'desactivar_morosos.py')

cmd_code = """from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.businesses.models import BusinessProfile

class Command(BaseCommand):
    help = 'Desactiva suscripciones vencidas automáticamente'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()
        self.stdout.write(f"🔍 Revisando vencimientos al: {hoy}")
        
        # Buscar negocios activos con fecha vencida
        vencidos = BusinessProfile.objects.filter(
            is_active_subscription=True, 
            subscription_end_date__lt=hoy
        )
        
        count = vencidos.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ Todo en orden. No hay cuentas por vencer.'))
            return

        self.stdout.write(f'⚠️ Encontrados {count} negocios vencidos. Procesando...')

        for negocio in vencidos:
            negocio.is_active_subscription = False
            negocio.save()
            self.stdout.write(self.style.WARNING(f'   🚫 Bloqueado: {negocio.business_name} (Venció: {negocio.subscription_end_date})'))

        self.stdout.write(self.style.SUCCESS(f'🏁 Proceso terminado. {count} cuentas suspendidas.'))
"""

with open(cmd_file_path, 'w', encoding='utf-8') as f:
    f.write(cmd_code)
print(f"✅ Comando creado en: {cmd_file_path}")

print("\n✨ ¡TODO LISTO! Ahora ejecuta:")
print("   1. python manage.py makemigrations businesses")
print("   2. python manage.py migrate")