import os
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
DETAIL_HTML = BASE_DIR / 'templates' / 'businesses' / 'detail.html'
HOME_HTML = BASE_DIR / 'templates' / 'home_landing.html' # Ajusta si usas home.html

def mejorar_detalle_negocio():
    print(f"🎨 Mejorando: {DETAIL_HTML}")
    if not DETAIL_HTML.exists():
        print(f"⚠️ No encontré {DETAIL_HTML}, saltando...")
        return

    with open(DETAIL_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. MEJORA: Etiqueta Inteligente de Abierto/Cerrado
    # Buscamos patrones comunes donde suele estar el estado
    # Reemplazamos la lógica vieja simple por la nueva inteligente
    
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
    
    # Intentamos encontrar donde ponerlo (generalmente cerca del nombre o rating)
    # Si encontramos un badge viejo, lo reemplazamos
    if "Abierto" in content and "badge" in content:
        import re
        # Busca un bloque div o span que contenga "Abierto"
        content = re.sub(r'<span[^>]*class="badge[^"]*"[^>]*>.*?Abierto.*?</span>', nuevo_badge, content, flags=re.DOTALL)
        print("   ✅ Badge de estado actualizado.")
    elif "</h1>" in content:
        # Si no, lo ponemos justo después del título del negocio
        content = content.replace("</h1>", "</h1>" + nuevo_badge)
        print("   ✅ Badge de estado insertado bajo el título.")

    # 2. MEJORA: Dirección Real
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

def agregar_geolocalizacion():
    # Intenta en home_landing.html primero, si no en home.html
    target_file = HOME_HTML
    if not target_file.exists():
        target_file = BASE_DIR / 'templates' / 'home.html'
    
    print(f"🌍 Agregando GPS en: {target_file}")
    if not target_file.exists():
        print("⚠️ No encontré archivo de home, saltando GPS...")
        return

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    script_gps = """
<script>
// --- GEOLOCALIZACIÓN AUTOMÁTICA (Auto-Inyectado) ---
document.addEventListener("DOMContentLoaded", function() {
    if (!sessionStorage.getItem("locationAsked")) {
        // Pequeño delay para no ser invasivo al cargar
        setTimeout(() => {
            if (confirm("¿Quieres ver los salones exclusivos cerca de tu ciudad? 📍")) {
                navigator.geolocation.getCurrentPosition(success, error);
                sessionStorage.setItem("locationAsked", "true");
            }
        }, 1000);
    }

    function success(position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        // Redirigir a búsqueda con coordenadas (ajusta la URL si es necesario)
        window.location.href = `/marketplace/?lat=${lat}&lng=${lng}`;
    }

    function error() {
        console.log("Ubicación denegada. Mostrando catálogo nacional.");
    }
});
</script>
"""
    # Insertar antes del cierre del body o del bloque principal
    if "{% endblock %}" in content:
        # Poner antes del último endblock (asumiendo que es el del contenido principal)
        parts = content.rsplit("{% endblock %}", 1)
        content = parts[0] + script_gps + "{% endblock %}" + parts[1]
        print("   ✅ Script de GPS inyectado.")
    elif "</body>" in content:
        content = content.replace("</body>", script_gps + "</body>")
        print("   ✅ Script de GPS inyectado al final del body.")
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    try:
        mejorar_detalle_negocio()
        agregar_geolocalizacion()
        print("\n✨ ¡Listo! Frontend actualizado automáticamente.")
    except Exception as e:
        print(f"❌ Error: {e}")