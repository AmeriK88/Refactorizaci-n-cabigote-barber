# Generated by Django 5.1.5 on 2025-01-20 22:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteDiario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.DateField(default=django.utils.timezone.now, verbose_name='Día')),
                ('total_citas', models.IntegerField(default=0, verbose_name='Total de citas')),
                ('ingresos_totales', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ingresos totales')),
                ('creado_el', models.DateTimeField(auto_now_add=True, verbose_name='Creado el')),
            ],
        ),
        migrations.CreateModel(
            name='ReporteMensual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes', models.DateField(default=django.utils.timezone.now, verbose_name='Mes')),
                ('total_citas', models.IntegerField(default=0, verbose_name='Total de citas')),
                ('ingresos_totales', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ingresos totales')),
                ('ingresos_proyectados', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ingresos proyectados')),
                ('creado_el', models.DateTimeField(auto_now_add=True, verbose_name='Creado el')),
            ],
        ),
    ]
