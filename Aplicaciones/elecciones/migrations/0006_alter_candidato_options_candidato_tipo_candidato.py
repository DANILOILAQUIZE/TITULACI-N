# Generated by Django 5.2 on 2025-06-10 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elecciones', '0005_candidato_padron'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='candidato',
            options={'ordering': ['lista', 'tipo_candidato', 'cargo']},
        ),
        migrations.AddField(
            model_name='candidato',
            name='tipo_candidato',
            field=models.CharField(choices=[('PRINCIPAL', 'Principal'), ('SUPLENTE', 'Suplente'), ('ALTERNO', 'Alterno'), ('OTRO', 'Otro')], default='PRINCIPAL', help_text='Tipo de candidato (Principal, Suplente, Alterno)', max_length=10),
        ),
    ]
