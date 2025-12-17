from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        # Esta línea asegura que se ejecute después de tu última migración
        ('businesses', '0006_employee_telegram_bot_token_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='description',
            field=models.TextField(blank=True, verbose_name='Descripción'),
        ),
    ]