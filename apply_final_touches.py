import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR FORMS.PY (Espacio para el ícono del ojo)
# ==========================================
# Necesitamos agregar padding a la derecha (pr-12) en los inputs de contraseña
# para que el texto no quede debajo del botón del ojo.
businesses_forms = """
from django import forms
from .models import Service, Salon, EmployeeSchedule
from apps.core.models import User
from datetime import time

def get_time_choices():
    choices = []
    for h in range(0, 24):
        for m in (0, 30):
            t = time(h, m)
            label = t.strftime('%I:%M %p')
            val = t.strftime('%H:%M')
            choices.append((val, label))
    return choices

TIME_CHOICES = get_time_choices()

COLOMBIA_CITIES = [
    ('Bogotá D.C.', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'), ('Pereira', 'Pereira'), ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'), ('Santa Marta', 'Santa Marta'), ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'), ('Tunja', 'Tunja'), ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'), ('Armenia', 'Armenia'), ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'), ('Sincelejo', 'Sincelejo'), ('Riohacha', 'Riohacha'),
    ('Zipaquirá', 'Zipaquirá'), ('Soacha', 'Soacha'), ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'), ('Bello', 'Bello'), ('Otro', 'Otro (Escribir en dirección)'),
]

class OwnerRegistrationForm(forms.ModelForm):
    salon_name = forms.CharField(label="Nombre del Negocio", required=True)
    salon_address = forms.CharField(label="Dirección del Local", required=True)
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad", required=True)
    phone = forms.CharField(label="WhatsApp (Soporte)", required=True)
    # AGREGADO pr-12 para el botón de ver contraseña
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********', 'class': 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm pr-12'}), required=True)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********', 'class': 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm pr-12'}), required=True)
    instagram_url = forms.URLField(label="Link Instagram", required=False)
    google_maps_url = forms.URLField(label="Link Google Maps", required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'OWNER'
        user.phone = self.cleaned_data["phone"]
        user.city = self.cleaned_data["city"]
        if commit:
            user.save()
            Salon.objects.create(
                owner=user,
                name=self.cleaned_data["salon_name"],
                address=self.cleaned_data["salon_address"],
                city=self.cleaned_data["city"],
                instagram_url=self.cleaned_data.get("instagram_url", ""),
                google_maps_url=self.cleaned_data.get("google_maps_url", ""),
                opening_time="08:00",
                closing_time="20:00"
            )
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['password1', 'password2']: # Evitamos sobrescribir la clase especial con padding
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm'

class OwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class SalonUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")
    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'instagram_url', 'google_maps_url']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=True)
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class SalonScheduleForm(forms.ModelForm):
    opening_time = forms.ChoiceField(choices=TIME_CHOICES, label="Apertura")
    closing_time = forms.ChoiceField(choices=TIME_CHOICES, label="Cierre")
    
    DAYS_CHOICES = [
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ]
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días de Apertura"
    )

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'active_days', 'deposit_percentage']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')
        
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        days = self.cleaned_data['active_days']
        return ','.join(days)

class EmployeeScheduleUpdateForm(forms.ModelForm):
    work_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio de Turno")
    work_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin de Turno")
    lunch_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio Almuerzo")
    lunch_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin Almuerzo")
    
    DAYS_CHOICES = [
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ]
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días Laborales"
    )

    class Meta:
        model = EmployeeSchedule
        fields = ['work_start', 'work_end', 'lunch_start', 'lunch_end', 'active_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')
            
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        days = self.cleaned_data['active_days']
        return ','.join(days)
"""

# ==========================================
# 2. LOGIN.HTML (OJO DE CONTRASEÑA)
# ==========================================
html_login = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-20 px-4 relative overflow-hidden bg-black">
    <div class="absolute inset-0 opacity-40">
        <img src="https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?q=80&w=2070&auto=format&fit=crop" class="w-full h-full object-cover">
    </div>
    
    <div class="glass-panel max-w-md w-full p-10 rounded-3xl shadow-2xl relative z-10 border border-white/10">
        <div class="text-center mb-10">
            <h2 class="text-3xl font-serif font-bold text-gray-900">Bienvenido</h2>
            <p class="mt-2 text-sm text-gray-500">Accede a tu panel de control</p>
        </div>

        <form class="space-y-6" method="post" action="{% url 'login' %}">
            {% csrf_token %}
            {% if form.errors %}
                <div class="bg-red-50 text-red-600 p-3 rounded text-sm text-center mb-4">Credenciales inválidas.</div>
            {% endif %}

            <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Usuario</label>
                <input type="text" name="username" required class="block w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:outline-none transition">
            </div>

            <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Contraseña</label>
                <div class="relative">
                    <input type="password" name="password" id="loginPass" required class="block w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:outline-none transition pr-12">
                    <button type="button" onclick="togglePassword('loginPass', this)" class="absolute inset-y-0 right-0 px-4 text-gray-400 hover:text-black focus:outline-none flex items-center">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                    </button>
                </div>
            </div>

            <button type="submit" class="w-full py-4 bg-black text-white font-bold rounded-xl hover:bg-gold transition duration-300 shadow-lg mt-4">
                INGRESAR
            </button>

            <div class="text-center mt-6 text-sm">
                <a href="{% url 'register_owner' %}" class="text-gray-500 hover:text-black transition">¿Nuevo aquí? <span class="font-bold underline">Crear cuenta</span></a>
            </div>
        </form>
    </div>
</div>

<script>
    function togglePassword(inputId, btn) {
        const input = document.getElementById(inputId);
        const icon = btn.querySelector('svg');
        if (input.type === "password") {
            input.type = "text";
            btn.classList.add('text-black');
            btn.classList.remove('text-gray-400');
        } else {
            input.type = "password";
            btn.classList.remove('text-black');
            btn.classList.add('text-gray-400');
        }
    }
</script>
{% endblock %}
"""

# ==========================================
# 3. REGISTER_OWNER.HTML (OJO DE CONTRASEÑA)
# ==========================================
html_register = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center py-20 px-4 relative overflow-hidden bg-gray-50">
    <div class="absolute top-0 left-0 w-full h-96 bg-black z-0"></div>
    
    <div class="max-w-3xl w-full bg-white p-10 md:p-14 rounded-3xl shadow-2xl relative z-10 border border-gray-100">
        <div class="text-center mb-10">
            <span class="text-gold font-bold tracking-widest text-xs uppercase">Registro Empresarial</span>
            <h2 class="mt-2 text-4xl font-serif font-bold text-gray-900">Crea tu Ecosistema</h2>
        </div>
        
        <form class="space-y-10" method="POST">
            {% csrf_token %}
            
            {% if form.errors %}
                <div class="bg-red-50 p-4 rounded-lg text-red-600 text-sm mb-6">
                    Por favor revisa los campos marcados.
                </div>
            {% endif %}

            <div>
                <h3 class="text-xl font-bold text-black border-b border-gray-100 pb-4 mb-6 flex items-center gap-2">
                    <span class="bg-black text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span> 
                    Datos del Propietario
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Nombre</label>{{ form.first_name }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Apellido</label>{{ form.last_name }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">WhatsApp</label>{{ form.phone }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Ciudad</label>{{ form.city }}</div>
                </div>
            </div>

            <div>
                <h3 class="text-xl font-bold text-black border-b border-gray-100 pb-4 mb-6 flex items-center gap-2">
                    <span class="bg-black text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">2</span> 
                    Datos del Negocio
                </h3>
                <div class="space-y-6">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Nombre del Establecimiento</label>{{ form.salon_name }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Dirección Física</label>{{ form.salon_address }}</div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Instagram (Opcional)</label>{{ form.instagram_url }}</div>
                        <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Google Maps (Opcional)</label>{{ form.google_maps_url }}</div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-50 p-8 rounded-2xl border border-gray-200">
                <h3 class="text-xl font-bold text-black border-b border-gray-200 pb-4 mb-6 flex items-center gap-2">
                    <span class="bg-black text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">3</span> 
                    Credenciales de Acceso
                </h3>
                <div class="grid grid-cols-1 gap-6">
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Usuario</label>{{ form.username }}</div>
                    <div><label class="block text-xs font-bold text-gray-500 uppercase mb-2">Email</label>{{ form.email }}</div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Contraseña</label>
                            <div class="relative">
                                {{ form.password1 }}
                                <button type="button" onclick="togglePassField(this)" class="absolute inset-y-0 right-0 px-4 text-gray-400 hover:text-black focus:outline-none flex items-center">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                                </button>
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Confirmar</label>
                            <div class="relative">
                                {{ form.password2 }}
                                <button type="button" onclick="togglePassField(this)" class="absolute inset-y-0 right-0 px-4 text-gray-400 hover:text-black focus:outline-none flex items-center">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <button type="submit" class="w-full py-5 bg-gold text-black font-bold rounded-xl hover:bg-black hover:text-white transition duration-500 shadow-xl text-lg tracking-widest uppercase">
                Finalizar Registro
            </button>
        </form>
    </div>
</div>

<script>
    function togglePassField(btn) {
        // Encontrar el input hermano anterior
        const input = btn.previousElementSibling;
        if (input && input.tagName === 'INPUT') {
            if (input.type === "password") {
                input.type = "text";
                btn.classList.add('text-black');
                btn.classList.remove('text-gray-400');
            } else {
                input.type = "password";
                btn.classList.remove('text-black');
                btn.classList.add('text-gray-400');
            }
        }
    }
</script>
{% endblock %}
"""

# ==========================================
# 4. BOOKING WIZARD (POLÍTICA DE CANCELACIÓN)
# ==========================================
html_booking = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-3xl">
        
        <div class="mb-8">
            <a href="{% url 'salon_detail' salon.pk %}" class="text-sm text-gray-500 hover:text-black mb-4 inline-block">&larr; Volver</a>
            <h1 class="text-3xl font-serif font-bold">Reserva tu experiencia</h1>
            <p class="text-gray-600">Servicio: <strong>{{ service.name }}</strong> (${{ service.price }})</p>
        </div>

        <form action="{% url 'booking_commit' %}" method="POST" id="bookingForm">
            {% csrf_token %}
            <input type="hidden" name="salon_id" value="{{ salon.id }}">
            <input type="hidden" name="service_id" value="{{ service.id }}">
            <input type="hidden" name="employee_id" id="selectedEmployee">
            <input type="hidden" name="time" id="selectedTime">

            <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
                
                <div class="p-8 border-b border-gray-100">
                    <h2 class="text-lg font-bold mb-4">1. Elige Especialista</h2>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {% for emp in employees %}
                        <label class="cursor-pointer group">
                            <input type="radio" name="employee_radio" value="{{ emp.id }}" class="peer sr-only" onchange="selectEmployee(this)">
                            <div class="p-4 rounded-xl border-2 border-gray-100 peer-checked:border-black peer-checked:bg-gray-50 transition-all text-center hover:border-gray-300">
                                <div class="w-12 h-12 bg-gray-200 rounded-full mx-auto mb-2 flex items-center justify-center font-bold text-gray-500">
                                    {{ emp.first_name|slice:":1" }}
                                </div>
                                <span class="text-sm font-bold block">{{ emp.first_name }}</span>
                            </div>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <div class="p-8 border-b border-gray-100 bg-gray-50 transition-opacity duration-300 opacity-50 pointer-events-none" id="step2">
                    <h2 class="text-lg font-bold mb-4">2. Selecciona Fecha y Hora</h2>
                    
                    <div class="mb-6">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Fecha</label>
                        <input type="date" name="date" id="datePicker" min="{{ today }}" value="{{ today }}" 
                               class="block w-full px-4 py-3 rounded-lg border-gray-300 shadow-sm focus:ring-black focus:border-black"
                               onchange="fetchSlots()">
                    </div>

                    <div id="slotsContainer" class="grid grid-cols-3 md:grid-cols-5 gap-3">
                        <p class="text-sm text-gray-400 col-span-5">Selecciona un empleado para ver horarios.</p>
                    </div>
                </div>

                {% if is_guest %}
                <div class="p-8 border-b border-gray-100 bg-white transition-opacity duration-300 opacity-50 pointer-events-none" id="step3">
                    <h2 class="text-lg font-bold mb-4">3. Tus Datos (Registro Automático)</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">Nombre</label>
                            <input type="text" name="first_name" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">Apellido</label>
                            <input type="text" name="last_name" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">WhatsApp</label>
                            <input type="text" name="phone" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 mb-1">Correo Electrónico</label>
                            <input type="email" name="email" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-black focus:border-black">
                        </div>
                    </div>
                </div>
                {% endif %}

                <div class="px-8 pb-4 pt-4 bg-gray-50 border-t border-gray-100">
                    <label class="flex items-start gap-3 cursor-pointer group p-4 bg-white rounded-lg border border-gray-200 hover:border-black transition">
                        <input type="checkbox" required class="mt-1 w-5 h-5 text-black border-gray-300 rounded focus:ring-black cursor-pointer">
                        <span class="text-sm text-gray-600 leading-tight">
                            He leído y acepto la <span class="font-bold text-black">Política de Cancelación</span>: Si no cumplo la cita, pierdo el abono. Si deseo reagendar, debo avisar con mínimo <span class="font-bold text-black">4 horas</span> de antelación.
                        </span>
                    </label>
                </div>

                <div class="px-8 pb-8 pt-4 flex justify-between items-center bg-gray-50 rounded-b-2xl">
                    <div>
                        <p class="text-xs text-gray-500 uppercase font-bold">Abono requerido</p>
                        <p class="text-2xl font-bold font-mono text-green-600">${{ deposit_amount }}</p>
                    </div>
                    <button type="submit" id="submitBtn" disabled class="bg-gray-300 text-white px-8 py-4 rounded-xl font-bold shadow-none cursor-not-allowed transition-all">
                        Pagar Abono y Confirmar
                    </button>
                </div>
            </div>
        </form>

    </div>
</div>

<script>
    let currentEmployee = null;

    function selectEmployee(radio) {
        currentEmployee = radio.value;
        document.getElementById('selectedEmployee').value = currentEmployee;
        
        const step2 = document.getElementById('step2');
        step2.classList.remove('opacity-50', 'pointer-events-none');
        step2.classList.add('bg-white');
        
        fetchSlots();
    }

    function fetchSlots() {
        if (!currentEmployee) return;
        
        const date = document.getElementById('datePicker').value;
        const container = document.getElementById('slotsContainer');
        container.innerHTML = '<p class="text-sm text-gray-500 col-span-5 animate-pulse">Buscando disponibilidad...</p>';

        fetch(`{% url 'api_get_slots' %}?salon_id={{ salon.id }}&service_id={{ service.id }}&employee_id=${currentEmployee}&date=${date}`)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = '';
                if (data.slots.length === 0) {
                    container.innerHTML = '<p class="text-sm text-red-500 col-span-5">No hay disponibilidad para esta fecha.</p>';
                    return;
                }

                data.slots.forEach(slot => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = `py-2 px-4 rounded-lg text-sm border-2 transition-all ${
                        slot.available 
                        ? 'bg-white border-gray-200 hover:border-black focus:bg-black focus:text-white' 
                        : 'bg-gray-100 border-transparent text-gray-400 cursor-not-allowed'
                    }`;
                    btn.innerText = slot.label;
                    btn.disabled = !slot.available;
                    
                    if (slot.available) {
                        btn.onclick = () => selectTime(slot.time, btn);
                    }
                    
                    container.appendChild(btn);
                });
            });
    }

    function selectTime(time, btnElement) {
        const buttons = document.getElementById('slotsContainer').getElementsByTagName('button');
        for(let b of buttons) {
            if(!b.disabled) {
                b.classList.remove('bg-black', 'text-white', 'border-black');
                b.classList.add('bg-white', 'text-black', 'border-gray-200');
            }
        }
        
        btnElement.classList.remove('bg-white', 'text-black', 'border-gray-200');
        btnElement.classList.add('bg-black', 'text-white', 'border-black');

        document.getElementById('selectedTime').value = time;
        
        const step3 = document.getElementById('step3');
        const submitBtn = document.getElementById('submitBtn');
        
        if (step3) {
            step3.classList.remove('opacity-50', 'pointer-events-none');
            step3.scrollIntoView({behavior: "smooth"});
        }
        
        submitBtn.disabled = false;
        submitBtn.classList.remove('bg-gray-300', 'shadow-none', 'cursor-not-allowed');
        submitBtn.classList.add('bg-black', 'shadow-lg', 'hover:scale-105');
    }
</script>
{% endblock %}
"""

def execute_final_touches():
    print("🎨 APLICANDO TOQUES FINALES DE USABILIDAD...")

    # 1. Update Forms (Padding para password)
    with open(BASE_DIR / 'apps' / 'businesses' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(businesses_forms.strip())
    print("✅ apps/businesses/forms.py: Widgets actualizados.")

    # 2. Update Login (Eye Icon)
    with open(BASE_DIR / 'templates' / 'registration' / 'login.html', 'w', encoding='utf-8') as f:
        f.write(html_login.strip())
    print("✅ templates/registration/login.html: Botón ver contraseña agregado.")

    # 3. Update Register Owner (Eye Icon)
    with open(BASE_DIR / 'templates' / 'registration' / 'register_owner.html', 'w', encoding='utf-8') as f:
        f.write(html_register.strip())
    print("✅ templates/registration/register_owner.html: Botones ver contraseña agregados.")

    # 4. Update Booking Wizard (Policy Checkbox)
    with open(BASE_DIR / 'templates' / 'marketplace' / 'booking_wizard.html', 'w', encoding='utf-8') as f:
        f.write(html_booking.strip())
    print("✅ templates/marketplace/booking_wizard.html: Política de cancelación insertada.")

if __name__ == "__main__":
    execute_final_touches()