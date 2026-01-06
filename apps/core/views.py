
from django.shortcuts import render, redirect
from django.contrib.auth import login
from apps.businesses.forms import OwnerRegistrationForm

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.user.is_authenticated:
        return redirect('businesses:dashboard')
        
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login
            return redirect('businesses:dashboard')
    else:
        form = OwnerRegistrationForm()
        
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    # Placeholder login logic (Django auth views should be used in prod urls)
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='registration/login.html')(request)
