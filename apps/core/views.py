from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .forms import OwnerRegistrationForm
from .models import User

class LandingPageView(TemplateView):
    template_name = "home.html"

class OwnerRegisterView(CreateView):
    model = User
    form_class = OwnerRegistrationForm
    template_name = "registration/register_owner.html"
    success_url = reverse_lazy('login') # Por ahora al login, luego al Dashboard

    def form_valid(self, form):
        messages.success(self.request, "¡Registro exitoso! Tienes 24 horas para activar tu cuenta.")
        return super().form_valid(form)
