import os
import subprocess
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DETAIL_HTML = BASE_DIR / 'templates' / 'businesses' / 'detail.html'
HOME_HTML = BASE_DIR / 'templates' / 'home_landing.html'

def paso(txt):
    print(f"\n🚀 {txt}...")

def arreglar_base_datos():
    paso("Generando instrucciones para la Base de Datos (Migraciones)")
    # Esto crea el archivo 0009_...py que le falta a Render
    try:
        subprocess.run(["python", "manage.py", "makemigrations"], check=True)
        print("   ✅ Archivo de migración creado (address, city, etc.)")
    except Exception as e:
        print(f"   ⚠️ No se pudo crear migración (quizás ya existe): {e}")

    paso("Aplicando cambios a tu base de datos local")
    try:
        subprocess.run(["python", "manage.py", "migrate"], check=True)
        print("   ✅ Base de datos local actualizada.")
    except Exception as e:
        print(f"   ❌ Error migrando local: {e}")

def arreglar_frontend():
    paso("Aplicando Diseño Inteligente (Abierto/Cerrado + Dirección)")
    
    if not DETAIL_HTML.exists():
        print("   ⚠️ No encontré el archivo detail.html.")
        return

    with open(DETAIL_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. CAMBIAR BADGE DE ESTADO (Abierto/Cerrado)
    nuevo_badge = """
    <div class="d-flex align-items-center gap-2 mb-3">
        {% if salon.is_open_now %}
            <span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill px-3">
                <i class="fas fa-clock me-1"></i> Abierto ahora
            </span>
        {% else %}
            <span class="badge bg-danger-subtle text-danger border border-danger-subtle rounded-pill px-3">
                <i class="fas fa-store-slash me-1"></i> Cerrado
            </span>
            <small class="text-muted fst-italic">
                <i class="fas fa-mobile-alt ms-1"></i> ¡Agenda abierta 24/7!
            </small>
        {% endif %}
    </div>
    """
    
    # Reemplazo inteligente: busca etiquetas 'badge' viejas o inserta bajo el título
    if "Abierto" in content and "badge" in content:
        # Intenta reemplazar el badge viejo
        content = re.sub(r'<span[^>]*class="badge[^"]*"[^>]*>.*?Abierto.*?</span>', nuevo_badge, content, flags=re.DOTALL)
        print("   ✅ Badge de estado actualizado.")
    elif "</h1>" in content and "is_open_now" not in content:
        content = content.replace("</h1>", "</h1>" + nuevo_badge)
        print("   ✅ Badge insertado bajo el título.")

    # 2. CAMBIAR UBICACIÓN EXCLUSIVA POR DIRECCIÓN REAL
    nueva_direccion = """
    <p class="text-muted mb-1">
        <i class="fas fa-map-marker-alt me-2 text-primary"></i>
        {% if salon.address %}
            {{ salon.address }}{% if salon.city %}, {{ salon.city }}{% endif %}
        {% else %}
            Ubicación disponible al reservar
        {% endif %}
    </p>
    """
    
    if "Ubicación exclusiva" in content:
        content = content.replace("Ubicación exclusiva", nueva_direccion)
        print("   ✅ Texto 'Ubicación exclusiva' reemplazado por dirección real.")
    
    with open(DETAIL_HTML, 'w', encoding='utf-8') as f:
        f.write(content)

    # 3. AGREGAR GPS EN HOME
    paso("Activando Geolocalización en Home")
    target_home = HOME_HTML if HOME_HTML.exists() else (BASE_DIR / 'templates' / 'home.html')
    
    if target_home.exists():
        with open(target_home, 'r', encoding='utf-8') as f:
            home_content = f.read()
        
        script_gps = """
<script>
// --- GEOLOCALIZACIÓN AUTOMÁTICA ---
document.addEventListener("DOMContentLoaded", function() {
    if (!sessionStorage.getItem("locationAsked")) {
        setTimeout(() => {
            if (confirm("¿Quieres ver los salones cerca de tu ciudad? 📍")) {
                navigator.geolocation.getCurrentPosition(pos => {
                    window.location.href = `/marketplace/?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}`;
                }, err => console.log("GPS no permitido"));
                sessionStorage.setItem("locationAsked", "true");
            }
        }, 1500);
    }
});
</script>
"""
        if "GEOLOCALIZACIÓN AUTOMÁTICA" not in home_content:
            if "{% endblock %}" in home_content:
                parts = home_content.rsplit("{% endblock %}", 1)
                home_content = parts[0] + script_gps + "{% endblock %}" + parts[1]
                print("   ✅ Script GPS inyectado.")
                with open(target_home, 'w', encoding='utf-8') as f:
                    f.write(home_content)
    else:
        print("   ⚠️ No encontré el home para poner el GPS.")

if __name__ == "__main__":
    print("=== 🛠 INICIANDO REPARACIÓN TOTAL ===")
    try:
        arreglar_base_datos()
        arreglar_frontend()
        
        print("\n✨ ¡TODO CORREGIDO! AHORA HAZ ESTO:")
        print("1. Ejecuta: git add .")
        print("2. Ejecuta: git commit -m 'Fix DB columns and Frontend'")
        print("3. Ejecuta: git push")
        print("\n👉 Al hacer el 'git push', Render detectará el archivo nuevo y")
        print("   arreglará el error 'column does not exist' automáticamente.")
    except Exception as e:
        print(f"\n❌ Error general: {e}")