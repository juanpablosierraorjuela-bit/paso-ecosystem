import os
from django.core.wsgi import get_wsgi_application

# Apuntamos a la configuración local
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

application = get_wsgi_application()