import os

def main():
    file_path = 'apps/core/models.py'
    print(f"🔧 REPARANDO CONEXIÓN EN: {file_path}")

    if not os.path.exists(file_path):
        print("❌ Error: No encuentro apps/core/models.py")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # El cambio: De BusinessProfile a Salon
    old_ref = "'businesses.BusinessProfile'"
    new_ref = "'businesses.Salon'"

    if old_ref in content:
        new_content = content.replace(old_ref, new_ref)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print("✅ ¡Conexión Reparada! Se cambió BusinessProfile por Salon.")
        print("\n👉 EJECUTA AHORA EN ORDEN:")
        print("   1. python manage.py makemigrations")
        print("   2. python manage.py migrate")
        print("   3. git add .")
        print("   4. git commit -m 'Fix: Update User model to link with Salon'")
        print("   5. git push origin main")
    else:
        print("⚠️ No encontré la referencia a BusinessProfile. ¿Quizás ya la cambiaste?")
        # Verificamos si ya dice Salon
        if new_ref in content:
            print("   ¡Sí! Ya apunta a 'businesses.Salon'. El archivo está bien.")
        else:
            print("   Revisa el archivo manualmente, algo raro pasa.")

if __name__ == "__main__":
    main()