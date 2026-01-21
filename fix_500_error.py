import os

def repair():
    print("--- Iniciando Reparación de Emergencia ---")

    # 1. ARREGLAR FORMS.PY (Añadir SalonScheduleForm que falta)
    forms_path = "apps/businesses/forms.py"
    salon_schedule_form_code = """

class SalonScheduleForm(forms.ModelForm):
    active_days = forms.MultipleChoiceField(
        choices=[('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'active_days', 'deposit_percentage']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        return ','.join(self.cleaned_data.get('active_days', []))
"""
    
    if os.path.exists(forms_path):
        with open(forms_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "SalonScheduleForm" not in content:
            with open(forms_path, "a", encoding="utf-8") as f:
                f.write(salon_schedule_form_code)
            print("✅ SalonScheduleForm añadido a forms.py")
        else:
            print("ℹ️ SalonScheduleForm ya existía.")

    # 2. ASEGURAR __INIT__.PY EN TEMPLATETAGS
    tags_dir = "apps/businesses/templatetags"
    os.makedirs(tags_dir, exist_ok=True)
    init_path = os.path.join(tags_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f: f.write("")
        print("✅ Archivo __init__.py creado en templatetags")

    # 3. VERIFICAR EL FILTRO CUSTOM_FILTERS.PY
    filter_path = os.path.join(tags_dir, "custom_filters.py")
    filter_code = """from django import template
register = template.Library()

@register.filter
def split_day(value):
    try:
        if ':' in value:
            parts = value.split(':')
            return {'index': parts[0], 'number': parts[1]}
    except:
        pass
    return {'index': 0, 'number': ''}
"""
    with open(filter_path, "w", encoding="utf-8") as f:
        f.write(filter_code)
    print("✅ Filtro split_day verificado/reparado.")

    print("--- Reparación completada. Reinicia el servidor con 'python manage.py runserver' ---")

if __name__ == "__main__":
    repair()