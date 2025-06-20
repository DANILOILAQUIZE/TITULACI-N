# Generated by Django 5.2 on 2025-06-19 20:29

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Noticia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('contenido', models.TextField(verbose_name='Contenido')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='noticias/', verbose_name='Imagen de portada')),
                ('fecha_publicacion', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de publicación')),
                ('estado', models.BooleanField(default=False, verbose_name='Publicado')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
            ],
            options={
                'verbose_name': 'Noticia',
                'verbose_name_plural': 'Noticias',
                'ordering': ['-fecha_publicacion'],
            },
        ),
    ]
