from .models import PlatformSettings
from django.db.utils import OperationalError, ProgrammingError

def global_settings(request):
    settings = None
    try:
        # Intentamos buscar la configuración
        settings = PlatformSettings.objects.first()
    except (OperationalError, ProgrammingError):
        # Si la tabla no existe (porque faltan migraciones), no hacemos nada
        # Esto evita el Error 500
        settings = None
    except Exception as e:
        # Cualquier otro error, lo ignoramos para mantener el sitio arriba
        settings = None
        
    return {'global_settings': settings}
