import os
from pathlib import Path

# Ruta al archivo de URLs principal
path = Path("config/urls.py")

def activar_ruta():
    print(f"🗺️  Configurando mapa de rutas en: {path}")
    
    if not path.exists():
        print("❌ Error: No encuentro config/urls.py")
        return

    content = path.read_text(encoding="utf-8")

    # 1. Asegurar que la vista esté importada
    if "bold_webhook" not in content:
        # Buscamos donde se importan las vistas de businesses
        if "from apps.businesses.views import (" in content:
            content = content.replace("from apps.businesses.views import (", "from apps.businesses.views import (\n    bold_webhook,")
            print("   ✅ Importación 'bold_webhook' agregada.")
        elif "from apps.businesses.views import" in content:
             # Si es importación simple
             content = content.replace("from apps.businesses.views import", "from apps.businesses.views import bold_webhook,")
             print("   ✅ Importación agregada (formato simple).")
    
    # 2. Agregar la ruta a urlpatterns
    ruta_webhook = "path('api/webhooks/bold/<int:salon_id>/', bold_webhook, name='bold_webhook'),"
    
    if "api/webhooks/bold" not in content:
        # Buscamos el inicio de urlpatterns
        if "urlpatterns = [" in content:
            content = content.replace("urlpatterns = [", f"urlpatterns = [\n    {ruta_webhook}")
            print("   ✅ Ruta '/api/webhooks/bold/...' registrada en el mapa.")
        else:
            print("   ⚠️ No encontré 'urlpatterns'. Revisa el archivo manualmente.")
    else:
        print("   ℹ️ La ruta ya existía.")

    path.write_text(content, encoding="utf-8")
    print("✨ ¡Mapa de rutas actualizado!")

if __name__ == "__main__":
    activar_ruta()