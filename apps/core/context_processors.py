from .models import GlobalSettings

def global_settings(request):
    settings = GlobalSettings.objects.first()
    return {'global_settings': settings}