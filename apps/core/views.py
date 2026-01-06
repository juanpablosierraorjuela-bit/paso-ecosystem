from django.shortcuts import render, redirect

def home(request):
    return render(request, 'home.html')
def register_owner(request):
    return render(request, 'registration/register_owner.html') # Placeholder
def login_view(request):
    return render(request, 'registration/login.html') # Placeholder