# Generated by Django 5.1.1 on 2025-01-03 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='apellido',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nombre',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
