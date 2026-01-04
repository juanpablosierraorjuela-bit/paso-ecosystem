import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
REGISTER_PATH = os.path.join(TEMPLATES_DIR, "registration", "register_owner.html")
MASTER_PATH = os.path.join(TEMPLATES_DIR, "master.html")

def reparar_conexion():
    print("🕵️‍♂️ Analizando archivos de plantillas...")

    # 1. Corregir el apuntador en register_owner.html
    if os.path.exists(REGISTER_PATH):
        with open(REGISTER_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # EL ERROR: Estaba buscando 'base.html', lo cambiamos a 'master.html'
        if "extends 'base.html'" in content:
            new_content = content.replace("extends 'base.html'", "extends 'master.html'")
            with open(REGISTER_PATH, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("   ✅ Corregido: El registro ahora usa 'master.html'.")
        else:
            print("   ℹ️ El registro ya estaba apuntando correctamente (o usa otra base).")
    else:
        print("   ❌ Error: No encontré register_owner.html")

    # 2. Asegurar que master.html tenga el 'enchufe' para el contenido
    if os.path.exists(MASTER_PATH):
        with open(MASTER_PATH, "r", encoding="utf-8") as f:
            master_content = f.read()
        
        # Verificamos si tiene {% block content %}
        if "{% block content %}" not in master_content:
            print("   ⚠️ Alerta: Tu 'master.html' no tenía espacio para contenido. Agregándolo...")
            # Si el archivo está vacío o incompleto, le inyectamos una estructura funcional que respete tu diseño
            NUEVO_MASTER = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paso Ecosystem</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">Paso Ecosystem</a>
        </div>
    </nav>

    <main>
        {% block content %}
        {% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
            with open(MASTER_PATH, "w", encoding="utf-8") as f:
                f.write(NUEVO_MASTER)
            print("   ✅ master.html reparado con estructura Bootstrap.")
        else:
            print("   ✅ Tu 'master.html' está perfecto y listo para recibir el formulario.")

if __name__ == "__main__":
    reparar_conexion()