from django import forms
from datetime import datetime, time
from django.utils import timezone

from .models import Cita, Servicio  

# Formulario cita
class CitaForm(forms.ModelForm):
    HORA_CHOICES = [
        ('', 'Seleccione una hora'),
        ('09:30', '09:30 AM'),
        ('10:00', '10:00 AM'),
        ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'),
        ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'),
        ('12:30', '12:30 PM'),
        ('16:00', '04:00 PM'),
        ('16:30', '04:30 PM'),
        ('17:00', '05:00 PM'),
        ('17:30', '05:30 PM'),
        ('18:00', '06:00 PM'),
        ('18:30', '06:30 PM'),
        ('19:00', '07:00 PM'),
        ('19:30', '07:30 PM'),
    ]

    hora = forms.ChoiceField(choices=HORA_CHOICES, label='Hora')
    servicio = forms.ModelChoiceField(queryset=Servicio.objects.all(), label='Servicio')
    # Campos para el formulario
    class Meta:
        model = Cita
        fields = ['servicio', 'fecha', 'hora', 'comentario']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
    # Manejo errores formulario
    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha.weekday() >= 5:
            raise forms.ValidationError("¡Puntalillo! Te recuerdo que el finde no curro.")
        today = timezone.now().date() 

        if fecha.date() < today:
            raise forms.ValidationError("¡Ñooosss! ¡Se te fue el baifo! La fecha ya pasó.")
        return fecha
    
    # Autor: José Félix Gordo Castaño
    # Copyright (C) 2024 José Félix Gordo Castaño
    # Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
    # No se permite la venta ni el uso comercial sin autorización expresa del autor.

    def clean_hora(self):
        hora = self.cleaned_data.get('hora')
        if not hora or hora == '':
            raise forms.ValidationError("Por favor, selecciona una hora válida.")
        
        hora = datetime.strptime(hora, '%H:%M').time()
        if hora < time(9, 30) or hora > time(19, 30):
            raise forms.ValidationError("¡Se te fue el baifo! La hora está fuera del rango.")
        return hora