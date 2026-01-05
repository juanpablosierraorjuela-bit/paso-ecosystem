from .models import PlatformSettings

def global_settings(request):
    """
    Inyecta la configuración global en todos los templates.
    """
    settings = PlatformSettings.objects.first()
    return {'PASO_SETTINGS': settings}
