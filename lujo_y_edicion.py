import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def actualizar_forms():
    path = BASE_DIR / 'apps' / 'businesses' / 'forms.py'
    print(f"📝 Habilitando edición de nombre en: {path}")
    
    if not path.exists():
        print("❌ No encontré forms.py")
        return

    content = path.read_text(encoding='utf-8')

    # 1. Agregar 'name' a la lista de campos permitidos
    # Buscamos la lista fields = [...] y le agregamos 'name' al principio si no está
    if "'name'" not in content and '"name"' not in content:
        content = content.replace("fields = ['address'", "fields = ['name', 'address'")
        print("   ✅ Campo 'Nombre' agregado a la lista de permitidos.")

    # 2. Agregar el widget para que se vea bonito en el HTML
    # Buscamos el inicio de widgets = {
    if "'name': forms.TextInput" not in content:
        widget_code = "'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de tu Negocio'}),"
        content = content.replace("widgets = {", f"widgets = {{\n            {widget_code}")
        print("   ✅ Diseño del campo 'Nombre' agregado.")

    path.write_text(content, encoding='utf-8')

def actualizar_html_dashboard():
    path = BASE_DIR / 'templates' / 'owner_dashboard.html'
    print(f"🎨 Aplicando Favicon y Campos en: {path}")
    
    if not path.exists():
        print("❌ No encontré owner_dashboard.html")
        return

    content = path.read_text(encoding='utf-8')

    # --- 1. FAVICON DE LUJO (P Negra Estilo Vogue) ---
    # Usamos un SVG en base64 para no tener que subir archivos de imagen
    favicon_lujo = """
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><circle cx=%2250%22 cy=%2250%22 r=%2250%22 fill=%22%23f0f0f0%22/><text x=%2250%22 y=%2250%22 font-family=%22Didot, serif%22 font-weight=%22bold%22 font-size=%2265%22 fill=%22black%22 text-anchor=%22middle%22 dy=%22.35em%22>P</text></svg>">
    <title>Panel Dueño | PASO</title>
    """
    
    # Insertar en el <head> si no está
    if "<link rel=\"icon\"" not in content:
        # Buscamos donde ponerlo, idealmente antes de cerrar head o al principio de block content si extiende
        if "{% block content %}" in content:
            # Si extiende base, lo ponemos al principio del bloque
            content = content.replace("{% block content %}", "{% block content %}\n" + favicon_lujo)
        else:
            # Si es archivo puro
            content = favicon_lujo + "\n" + content
        print("   ✅ Favicon 'P' de lujo instalado.")

    # --- 2. AGREGAR CAMPO DE NOMBRE EN EL FORMULARIO ---
    # Buscamos el formulario de configuración
    marker = "" # Usamos texto cercano para ubicar
    
    # Buscamos dónde empieza el formulario de Ubicación (generalmente el primero)
    if "{{ config_form.name }}" not in content:
        # Insertamos el campo de nombre antes de la Dirección
        bloque_nombre = """
        <div class="mb-4">
            <label class="form-label fw-bold">Nombre del Negocio</label>
            {{ config_form.name }}
        </div>
        """
        
        # Buscamos la etiqueta de "Ubicación del Negocio" para poner el Nombre antes
        if "UBICACIÓN DEL NEGOCIO" in content:
            content = content.replace("📍 UBICACIÓN DEL NEGOCIO", bloque_nombre + "\n\n            📍 UBICACIÓN DEL NEGOCIO")
            print("   ✅ Campo para editar Nombre insertado en el panel.")
        elif "{{ config_form.address }}" in content:
             content = content.replace("{{ config_form.address }}", bloque_nombre + "\n{{ config_form.address }}")
             print("   ✅ Campo Nombre insertado (método alternativo).")

    path.write_text(content, encoding='utf-8')

def actualizar_html_home():
    # También ponemos el favicon en el home para que se vea lindo al entrar
    path = BASE_DIR / 'templates' / 'home.html'
    if path.exists():
        content = path.read_text(encoding='utf-8')
        favicon_lujo = """<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><circle cx=%2250%22 cy=%2250%22 r=%2250%22 fill=%22%23f0f0f0%22/><text x=%2250%22 y=%2250%22 font-family=%22Didot, serif%22 font-weight=%22bold%22 font-size=%2265%22 fill=%22black%22 text-anchor=%22middle%22 dy=%22.35em%22>P</text></svg>">"""
        
        if "<link rel=\"icon\"" not in content:
             if "<head>" in content:
                 content = content.replace("<head>", "<head>\n" + favicon_lujo)
             elif "{% load static %}" in content:
                 content = content.replace("{% load static %}", "{% load static %}\n" + favicon_lujo)
             path.write_text(content, encoding='utf-8')
             print("   ✅ Favicon agregado al Home.")

if __name__ == "__main__":
    actualizar_forms()
    actualizar_html_dashboard()
    actualizar_html_home()
    print("\n✨ ¡LISTO! Modificaciones cosméticas aplicadas con seguridad quirúrgica.")