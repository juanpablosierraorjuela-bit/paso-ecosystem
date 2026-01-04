from .models import PlatformSettings
from django.db.utils import OperationalError, ProgrammingError

def global_settings(request):
    settings = None
    try:
        # Intenta obtener la configuración
        settings = PlatformSettings.objects.first()
    except (OperationalError, ProgrammingError):
        # Si la tabla no existe (error de migración), devuelve None y NO ROMPE la página
        settings = None
    except Exception:
        # Cualquier otro error, se ignora por seguridad
        settings = None
        
    return {'global_settings': settings}
