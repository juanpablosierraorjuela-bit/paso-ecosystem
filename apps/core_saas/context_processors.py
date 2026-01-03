from .models import PlatformSettings

def platform_settings(request):
    # Obtiene la primera configuración que encuentre
    settings = PlatformSettings.objects.first()
    return {'global_settings': settings}