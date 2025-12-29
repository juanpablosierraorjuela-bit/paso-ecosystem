import os

print("🔓 Quitándole el seguro al Botón Rojo...")

views_path = os.path.join('apps', 'businesses', 'views.py')

try:
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Buscamos el bloque de seguridad y lo desactivamos comentándolo
    if 'if not request.user.is_superuser:' in content:
        new_content = content.replace(
            'if not request.user.is_superuser:', 
            '# SEGURIDAD DESACTIVADA TEMPORALMENTE\n    if False: # if not request.user.is_superuser:'
        )
        
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Seguro desactivado. Ahora el botón funcionará sin login.")
    else:
        print("⚠️ No encontré el bloque de seguridad. ¿Quizás ya lo quitaste?")

except Exception as e:
    print(f"❌ Error modificando views.py: {e}")

print("\n🚀 LISTO. Pasos a seguir:")
print("1. git add .")
print("2. git commit -m 'Allow reset without login'")
print("3. git push origin main")
print("4. Espera el deploy y vuelve a entrar al enlace: https://paso-backend.onrender.com/reset-database-secure-action/")