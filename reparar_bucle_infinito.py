import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def arreglar_settings():
    path = BASE_DIR / 'config' / 'settings.py'
    print(f"🔧 Reparando configuración SSL en: {path}")
    
    if not path.exists():
        print("❌ No encontré settings.py")
        return

    content = path.read_text(encoding='utf-8')
    
    # Esta es la línea mágica que falta para que Render y Django se entiendan
    config_proxy = "SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')"
    
    if config_proxy not in content:
        # Lo agregamos al final del archivo
        content += f"\n\n# --- FIX DE BUCLE INFINITO RENDER ---\n{config_proxy}\n"
        path.write_text(content, encoding='utf-8')
        print("   ✅ Configuración de Proxy SSL agregada. El bucle se detendrá.")
    else:
        print("   ℹ️ La configuración ya estaba, revisa caché del navegador.")

if __name__ == "__main__":
    arreglar_settings()