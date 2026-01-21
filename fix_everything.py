import os

def fix():
    print("--- Iniciando Reparación Integral ---")

    # 1. CORREGIR FORMS.PY (Añadir los formularios que faltan)
    forms_path = "apps/businesses/forms.py"
    
    # Código base para los formularios que faltaban
    extra_forms = """

class OwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class SalonUpdateForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'description', 'instagram_url', 'bank_name', 'account_number']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
"""
    
    if os.path.exists(forms_path):
        with open(forms_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "OwnerUpdateForm" not in content:
            with open(forms_path, "a", encoding="utf-8") as f:
                f.write(extra_forms)
            print("✅ Formularios OwnerUpdateForm y SalonUpdateForm añadidos a forms.py")
        else:
            print("ℹ️ Los formularios ya existían en forms.py")
    else:
        print("❌ Error: No se encontró apps/businesses/forms.py")

    # 2. VERIFICAR MODELS.PY (Para EmployeeSchedule)
    # Algunos archivos de marketplace buscan 'EmployeeSchedule'
    models_path = "apps/businesses/models.py"
    if os.path.exists(models_path):
        with open(models_path, "r", encoding="utf-8") as f:
            models_content = f.read()
        
        # Si el modelo se llama 'EmployeeSchedule' en lugar de 'EmployeeBaseSchedule' o similar
        if "class EmployeeSchedule" not in models_content:
            print("⚠️ Advertencia: El modelo EmployeeSchedule no se encontró. Verifica si se llama diferente.")

    # 3. LIMPIEZA DE VIEWS.PY (Asegurar que el panel de empleado no falle)
    # Vamos a rodear la obtención del salón con un try/except por seguridad
    views_path = "apps/businesses/views.py"
    if os.path.exists(views_path):
        with open(views_path, "r", encoding="utf-8") as f:
            v_content = f.read()
        
        # Pequeño fix para evitar que falle si el empleado no tiene workplace asignado
        old_line = "salon = request.user.workplace if request.user.role == 'EMPLOYEE' else getattr(request.user, 'owned_salon', None)"
        new_line = "salon = getattr(request.user, 'workplace', None) if request.user.role == 'EMPLOYEE' else getattr(request.user, 'owned_salon', None)"
        
        if old_line in v_content:
            v_content = v_content.replace(old_line, new_line)
            with open(views_path, "w", encoding="utf-8") as f:
                f.write(v_content)
            print("✅ Vista de Dashboard protegida contra errores de Salón ausente.")

    print("--- Proceso completado ---")

if __name__ == "__main__":
    fix()