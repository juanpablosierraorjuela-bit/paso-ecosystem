from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0007_alter_employeeschedule_options_and_more'),
    ]

    operations = [
        # Ejecutamos SQL directo para borrar la columna que causa el conflicto
        migrations.RunSQL(
            "ALTER TABLE businesses_service DROP COLUMN IF EXISTS description;"
        ),
    ]
