from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('CLIENT', 'Cliente / Usuario'), ('EMPLOYEE', 'Colaborador / Estilista'), ('OWNER', 'Dueño de Negocio')],
                default='CLIENT',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]