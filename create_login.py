import os

# Contenido del Login con tus estilos actuales (landing.css)
login_content = """{% extends 'base.html' %}

{% block content %}
<div class="auth-container">
    <h2 style="text-align: center; margin-bottom: 30px; color: #d4af37;">Bienvenido de Nuevo</h2>
    
    <form method="post">
        {% csrf_token %}
        
        {% if form.errors %}
            <div style="color: #ff4d4d; background: rgba(255, 77, 77, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center;">
                Usuario o contraseña incorrectos.
            </div>
        {% endif %}

        <div class="form-group" style="margin-bottom: 15px;">
            <label for="id_username">Usuario o Email</label>
            <input type="text" name="username" autofocus autocapitalize="none" autocomplete="username" maxlength="150" required id="id_username" class="form-input" placeholder="Ingresa tu usuario">
        </div>

        <div class="form-group" style="margin-bottom: 15px;">
            <label for="id_password">Contraseña</label>
            <input type="password" name="password" autocomplete="current-password" required id="id_password" class="form-input" placeholder="••••••••">
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 10px;">
            Entrar al Ecosistema
        </button>
    </form>
    
    <div style="text-align: center; margin-top: 25px; border-top: 1px solid #333; padding-top: 20px;">
        <p style="color: #888; font-size: 0.9rem;">¿Eres dueño de negocio?</p>
        <a href="{% url 'register_owner' %}" class="btn-outline" style="font-size: 0.9rem; padding: 8px 20px; border-radius: 20px;">Registrar mi Negocio</a>
    </div>
</div>
{% endblock %}
"""

def main():
    # Ruta exacta donde Django busca el archivo
    file_path = 'templates/registration/login.html'
    
    # Aseguramos que la carpeta exista (aunque ya debería estar por register_owner.html)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Escribimos el archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(login_content)
    
    print(f"✅ Archivo creado exitosamente: {file_path}")
    print("👉 Ahora ejecuta: git add . && git commit -m 'Add: Login template' && git push origin main")

if __name__ == "__main__":
    main()