from .models import Salon
def owner_check(request):
    try:
        if request.user.is_authenticated:
            salon = Salon.objects.filter(owner=request.user).first()
            return {'is_owner': bool(salon), 'user_salon': salon}
    except: pass
    return {'is_owner': False}