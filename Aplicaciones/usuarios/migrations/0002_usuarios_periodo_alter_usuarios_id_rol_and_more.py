# Generated by Django 5.1.5 on 2025-04-08 04:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodo', '0001_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarios',
            name='periodo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='periodo.periodo'),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='id_rol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='usuarios.roles'),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='username',
            field=models.CharField(max_length=10, unique=True, verbose_name='Cédula'),
        ),
    ]
