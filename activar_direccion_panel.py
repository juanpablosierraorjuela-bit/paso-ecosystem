import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def actualizar_formulario():
    ruta_forms = BASE_DIR / 'apps' / 'businesses' / 'forms.py'
    print(f"📝 Actualizando formulario en: {ruta_forms}")
    
    with open(ruta_forms, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verificar si ya están los campos para no duplicar
    if "'address'" in content and "'city'" in content:
        print("   ℹ️ El formulario ya tiene dirección y ciudad.")
        return

    # 1. Agregar los campos a la lista 'fields'
    # Buscamos la línea que empieza con "fields = ["
    nuevo_fields = "fields = ['address', 'city', 'opening_time'"
    content = content.replace("fields = ['opening_time'", nuevo_fields)

    # 2. Agregar los widgets (estilos) para que se vean bonitos
    widgets_nuevos = """widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa (Ej: Cra 10 # 20-30)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'opening_time'"""
    
    content = content.replace("widgets = {\n            'opening_time'", widgets_nuevos)
    
    with open(ruta_forms, 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✅ Formulario actualizado con éxito.")

def actualizar_template_dashboard():
    ruta_html = BASE_DIR / 'templates' / 'owner_dashboard.html'
    print(f"🎨 Actualizando diseño en: {ruta_html}")
    
    with open(ruta_html, 'r', encoding='utf-8') as f:
        content = f.read()

    if "Dirección del Local" in content:
        print("   ℹ️ El diseño ya tiene el campo de dirección.")
        return

    # Bloque HTML a insertar (Limpio y con estilos Bootstrap)
    bloque_direccion = """
                            <h6 class="fw-bold text-muted text-uppercase mb-3 small ls-1">📍 Ubicación del Negocio</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-md-8">
                                    <div class="form-floating">
                                        {{ config_form.address }}
                                        <label>Dirección del Local</label>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="form-floating">
                                        {{ config_form.city }}
                                        <label>Ciudad</label>
                                    </div>
                                </div>
                            </div>

                            <h6 class="fw-bold text-muted text-uppercase mb-3 small ls-1">⏰ Horario General</h6>"""

    # Buscamos el título de Horario para insertar esto justo antes
    if "⏰ Horario General" in content:
        content = content.replace('<h6 class="fw-bold text-muted text-uppercase mb-3 small ls-1">⏰ Horario General</h6>', bloque_direccion)
        
        with open(ruta_html, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ Campos de dirección agregados al panel visual.")
    else:
        print("   ⚠️ No encontré la referencia exacta en el HTML. Revisa manualmente.")

if __name__ == "__main__":
    print("=== 🏗 INTEGRANDO DIRECCIÓN EN PANEL DE DUEÑO ===")
    try:
        actualizar_formulario()
        actualizar_template_dashboard()
        print("\n✨ ¡Listo! Sin romper nada.")
    except Exception as e:
        print(f"❌ Error: {e}")