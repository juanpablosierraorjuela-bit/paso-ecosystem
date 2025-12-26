import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def liberar_reservas():
    path = BASE_DIR / 'apps' / 'businesses' / 'views.py'
    print(f"🔓 Desbloqueando página de reservas en: {path}")
    
    if not path.exists():
        print("❌ No encontré views.py")
        return

    content = path.read_text(encoding='utf-8')
    
    # El bloque de código que causó el problema
    candado_mal_puesto = """
    # --- AUDITORIA DE SEGURIDAD ---
    if salon.owner != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("No tienes permiso para ver este salón.")
    # ------------------------------"""

    # Vamos a eliminarlo globalmente, ya que 'owner_dashboard' ya se protege solo
    # (usa filter(owner=user), así que no necesita este chequeo extra)
    
    # Normalizamos espacios para asegurarnos de encontrarlo
    # Usamos una regex flexible con los espacios
    patron = r'\s*# --- AUDITORIA DE SEGURIDAD ---.*?raise PermissionDenied\("No tienes permiso para ver este salón."\)\s*# ------------------------------'
    
    match = re.search(patron, content, re.DOTALL)
    
    if match:
        content = re.sub(patron, "", content, flags=re.DOTALL)
        path.write_text(content, encoding='utf-8')
        print("   ✅ ¡Candado eliminado! La página de reservas vuelve a ser pública.")
    else:
        print("   ℹ️ No encontré el bloqueo. Puede que ya se haya borrado o el código sea diferente.")
        # Intento de rescate manual: buscar partes clave por si los espacios cambiaron
        if "PermissionDenied" in content and "salon.owner != request.user" in content:
             print("   ⚠️ Detecté fragmentos del bloqueo. Intentando limpieza agresiva...")
             lines = content.split('\n')
             new_lines = []
             skip = False
             for line in lines:
                 if "# --- AUDITORIA DE SEGURIDAD ---" in line:
                     skip = True
                 if not skip:
                     new_lines.append(line)
                 if "# ------------------------------" in line and skip:
                     skip = False
             
             content = "\n".join(new_lines)
             path.write_text(content, encoding='utf-8')
             print("   ✅ Limpieza agresiva completada.")

if __name__ == "__main__":
    liberar_reservas()