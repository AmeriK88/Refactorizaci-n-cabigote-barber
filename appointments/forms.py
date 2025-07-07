from django import forms
from datetime import datetime, time
from django.utils import timezone
from .models import Cita, Servicio, Imagen
from django.contrib import admin


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

    # Producto opcional
    producto = forms.ModelChoiceField(
        queryset=Imagen.objects.all(),
        label='Producto (Opcional)',
        required=False,  # No obligatorio
    )

    # Personalizar cómo se muestra el servicio en el menú desplegable
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.all(),
        label='Servicio',
        empty_label="Seleccione un servicio",
        to_field_name='id',
        widget=forms.Select,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --------------------------
        # 1. Estiliza widgets → Bootstrap
        # --------------------------
        for name, field in self.fields.items():
            widget = field.widget
            base_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            # Concatena si ya tiene otras clases
            existing_cls = widget.attrs.get('class', '')
            widget.attrs['class'] = f"{existing_cls} {base_class}".strip()
            # Placeholder para floating labels (solo inputs, no selects)
            if not isinstance(widget, forms.Select):
                widget.attrs.setdefault('placeholder', field.label)

        # --------------------------
        # 2. Etiquetas amigables
        # --------------------------
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Personaliza cómo se muestran los servicios (nombre + precio)
            self.fields['servicio'].label_from_instance = lambda obj: f"{obj.nombre} - {obj.precio} €"

            # Mejora: evita el error 500 si obj.precio es None, mostrando "N/A" en ese caso
            self.fields['producto'].label_from_instance = (
                lambda obj: f"{obj.titulo} - €{obj.precio:.2f}"
                if obj.precio is not None else
                f"{obj.titulo} - €N/A"
            )
    # --------------------------
    # 3. Config Meta
    # --------------------------
    class Meta:
        model = Cita
        fields = ['servicio', 'producto', 'fecha', 'hora', 'comentario']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',  # asegura estilo en datepicker nativo
            }),
            'comentario': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Comentarios adicionales…',
            })
        }

    # --------------------------
    # 4. Validaciones personalizadas
    # --------------------------
    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha.weekday() >= 5:
            raise forms.ValidationError("¡Puntalillo! Te recuerdo que el finde no curro.")

        today = timezone.now().date()
        if fecha.date() < today:
            raise forms.ValidationError("¡Ñooosss! ¡Se te fue el baifo! La fecha ya pasó.")
        return fecha

    def clean_hora(self):
        hora = self.cleaned_data.get('hora')
        if not hora:
            raise forms.ValidationError("Por favor, selecciona una hora válida.")

        hora_obj = datetime.strptime(hora, '%H:%M').time()
        if hora_obj < time(9, 30) or hora_obj > time(19, 30):
            raise forms.ValidationError("¡Se te fue el baifo! La hora está fuera del rango.")
        return hora

    # Autor: José Félix Gordo Castaño
    # Copyright (C) 2024 José Félix Gordo Castaño
    # Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje.
    # No se permite la venta ni el uso comercial sin autorización expresa del autor.
