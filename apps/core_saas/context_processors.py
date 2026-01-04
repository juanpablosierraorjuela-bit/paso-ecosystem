from .models import PlatformSettings

def global_settings(request):
    # Busca la configuración, si no existe devuelve vacío para no romper nada
    settings = PlatformSettings.objects.first()
    return {'global_settings': settings}
