# Generated by Django 5.2 on 2025-05-13 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodo',
            name='estado',
            field=models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo', max_length=10),
        ),
    ]
