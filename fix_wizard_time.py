import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWS_PATH = os.path.join(BASE_DIR, "apps", "businesses", "views.py")

def corregir_wizard():
    print("⏰ Corrigiendo lógica de zonas horarias en el Wizard...")
    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Aseguramos que se use timezone.make_aware para evitar los Naive Datetime warnings
    old_code = "booking.date_time = datetime.combine(date, time)"
    new_code = "from django.utils import timezone\n            booking.date_time = timezone.make_aware(datetime.combine(date, time))"
    
    if old_code in content and "timezone.make_aware" not in content:
        content = content.replace(old_code, new_code)
        with open(VIEWS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print("   ✅ Lógica de tiempo actualizada.")
    else:
        print("   ℹ️ El código ya estaba actualizado o no se encontró el patrón.")

if __name__ == "__main__":
    corregir_wizard()