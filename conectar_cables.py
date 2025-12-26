import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def arreglar_views_imports():
    ruta = BASE_DIR / 'apps' / 'businesses' / 'views.py'
    print(f"🔧 Revisando importaciones en: {ruta}")
    
    content = ruta.read_text(encoding='utf-8')
    
    # Lista de importaciones obligatorias para el webhook
    imports_necesarios = [
        "from django.views.decorators.csrf import csrf_exempt",
        "from django.http import JsonResponse, HttpResponse",
        "import json",
        "from decimal import Decimal"
    ]
    
    nuevos_imports = []
    for imp in imports_necesarios:
        if imp not in content:
            nuevos_imports.append(imp)
    
    if nuevos_imports:
        # Insertar al principio del archivo
        content = "\n".join(nuevos_imports) + "\n" + content
        ruta.write_text(content, encoding='utf-8')
        print(f"   ✅ Se agregaron {len(nuevos_imports)} importaciones faltantes.")
    else:
        print("   ✅ Views.py ya tiene todas las importaciones correctas.")

def arreglar_urls():
    ruta = BASE_DIR / 'config' / 'urls.py'
    print(f"🗺️  Arreglando mapa de rutas en: {ruta}")
    
    content = ruta.read_text(encoding='utf-8')

    # 1. Asegurar importación de la vista
    if "bold_webhook" not in content:
        # Reemplazo genérico para cualquier forma de importar
        if "from apps.businesses.views import" in content:
            # Buscamos la línea y le agregamos bold_webhook
            import re
            content = re.sub(r'(from apps\.businesses\.views import .*?)(\))', r'\1, bold_webhook)', content, flags=re.DOTALL)
            # Si no usaba paréntesis, intentamos el otro método
            if "bold_webhook" not in content:
                 content = content.replace("from apps.businesses.views import", "from apps.businesses.views import bold_webhook,")
            print("   ✅ Importación de 'bold_webhook' agregada a urls.py.")

    # 2. Asegurar que la RUTA existe
    ruta_nueva = "    path('api/webhooks/bold/<int:salon_id>/', bold_webhook, name='bold_webhook'),"
    
    if "api/webhooks/bold" not in content:
        # Buscamos dónde termina la lista urlpatterns
        if "]" in content:
            # Insertamos antes del último corchete
            idx = content.rfind("]")
            content = content[:idx] + "\n" + ruta_nueva + "\n" + content[idx:]
            print("   ✅ Ruta '/api/webhooks/bold/...' insertada correctamente.")
        else:
            print("   ❌ NO PUDE INSERTAR LA RUTA. El archivo urls.py es extraño.")
    else:
        print("   ✅ La ruta ya existía en el mapa.")

    ruta.write_text(content, encoding='utf-8')

if __name__ == "__main__":
    print("=== 🔌 CONECTANDO CABLES DEL WEBHOOK ===")
    try:
        arreglar_views_imports()
        arreglar_urls()
        print("\n✨ ¡Listo! Ahora Django sabe dónde está la puerta.")
    except Exception as e:
        print(f"❌ Error crítico: {e}")