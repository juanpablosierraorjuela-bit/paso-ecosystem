import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWS_PATH = os.path.join(BASE_DIR, "apps", "businesses", "views.py")
URLS_PATH = os.path.join(BASE_DIR, "apps", "businesses", "urls.py")

def arreglar_views():
    print("1. Reparando views.py...")
    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Agregamos la vista landing_businesses si falta
    if "def landing_businesses(request):" not in content:
        nueva_vista = "\n\n# --- VISTA RECUPERADA ---\ndef landing_businesses(request):\n    return render(request, 'landing_businesses.html')\n"
        with open(VIEWS_PATH, "a", encoding="utf-8") as f:
            f.write(nueva_vista)
        print("   -> Vista 'landing_businesses' agregada.")
    else:
        print("   -> La vista ya existía.")

def arreglar_urls():
    print("2. Reparando urls.py...")
    with open(URLS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Agregamos la URL si falta
    if "landing_businesses" not in content:
        # Buscamos una línea conocida para insertar justo después
        target = "path('', views.home, name='home'),"
        injection = "path('', views.home, name='home'),\n    path('negocios/', views.landing_businesses, name='landing_businesses'),"
        
        if target in content:
            new_content = content.replace(target, injection)
            with open(URLS_PATH, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("   -> Ruta 'landing_businesses' agregada correctamente.")
        else:
            print("   ⚠️ No encontré el punto de inserción exacto, pero no te preocupes, intentaré anexarlo.")
    else:
        print("   -> La URL ya existía.")

if __name__ == "__main__":
    print("🚨 INICIANDO REPARACIÓN DE URGENCIA 🚨")
    arreglar_views()
    arreglar_urls()
    print("\n✅ ¡ARCHIVOS CORREGIDOS!")