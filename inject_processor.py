import os

settings_path = 'config/settings.py'
with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "'django.contrib.messages.context_processors.messages',"
new_line = "                'apps.core.context_processors.global_settings', # Footer Dinámico"

if new_line not in content:
    content = content.replace(target, target + '\n' + new_line)
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(" Context Processor añadido a settings.py")
else:
    print("ℹ Ya estaba configurado.")
