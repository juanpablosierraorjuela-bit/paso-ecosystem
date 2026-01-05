from .models import PlatformSettings
from django.db.utils import OperationalError, ProgrammingError

def platform_settings(request):
    settings = None
    try:
        settings = PlatformSettings.objects.first()
    except (OperationalError, ProgrammingError):
        settings = None
    except Exception:
        settings = None
        
    return {'global_settings': settings}
