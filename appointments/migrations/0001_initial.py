# Generated by Django 5.1.1 on 2024-10-31 12:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=6)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='servicios/')),
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
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appointments.servicio')),
            ],
        ),
    ]
