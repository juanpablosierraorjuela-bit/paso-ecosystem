import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paso_ecosystem.settings')
django.setup()

from apps.core_saas.models import User

# Configuración del Admin
USERNAME = 'juanpablo'
EMAIL = 'admin@pasotunja.com'
PASSWORD = 'admin123_secure'  # Cambia esto después si quieres

if not User.objects.filter(username=USERNAME).exists():
    print(f"Creating superuser {USERNAME}...")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print("✅ Superuser created successfully!")
else:
    print("⚠️ Superuser already exists.")
