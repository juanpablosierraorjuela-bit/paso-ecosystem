from .models import Salon

def owner_check(request):
    """
    Este código se ejecuta en TODAS las páginas.
    Verifica si el usuario logueado es dueño de algún salón.
    """
    is_owner = False
    salon_name = ""
    
    if request.user.is_authenticated:
        # Buscamos si existe al menos un salón propiedad de este usuario
        salon = Salon.objects.filter(owner=request.user).first()
        if salon:
            is_owner = True
            salon_name = salon.name
            
    # Devolvemos estas variables para usarlas en cualquier HTML
    return {
        'is_owner': is_owner,
        'my_salon_name': salon_name
    }