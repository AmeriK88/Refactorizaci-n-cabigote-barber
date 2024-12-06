# Generated by Django 5.1.1 on 2024-12-04 23:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FechaBloqueada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(unique=True, verbose_name='Fecha Bloqueada')),
                ('razon', models.CharField(blank=True, max_length=255, null=True, verbose_name='Razón')),
            ],
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
                ('hora', models.TimeField()),
                ('comentario', models.TextField(blank=True, null=True)),
                ('vista', models.BooleanField(default=False)),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.servicio')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]