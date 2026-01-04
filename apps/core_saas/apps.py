from django.apps import AppConfig

class CoreSaasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_saas'
    label = 'core_saas'  # <--- ¡ESTO FALTABA! Es la clave para que Django encuentre el User.
