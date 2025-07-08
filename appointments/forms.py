# appointments/forms.py
from django import forms
from datetime import datetime, time
from django.utils import timezone
from .models import Cita
from services.models import Servicio
from products.models import Imagen

# ------------------------------------------------------------------
# PERSONALIZED CHOICE FIELDS
# ------------------------------------------------------------------
class ServicioChoiceField(forms.ModelChoiceField):
    """Despliega nombre y precio del servicio."""
    def label_from_instance(self, obj):
        precio = "€N/A" if obj.precio is None else f"€{obj.precio:.2f}" # type: ignore[arg-type]
        return f"{obj.nombre} - {precio}" # type: ignore[arg-type]

class ImagenChoiceField(forms.ModelChoiceField):
    """Despliega título y precio del producto opcional."""
    def label_from_instance(self, obj):
        precio = "€N/A" if obj.precio is None else f"€{obj.precio:.2f}" # type: ignore[arg-type]
        return f"{obj.titulo} - {precio}" # type: ignore[arg-type]

# ------------------------------------------------------------------
# APPOINTMENT FORM
# ------------------------------------------------------------------
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

    servicio = ServicioChoiceField(
        queryset=Servicio.objects.all(),
        label='Servicio',
        empty_label='Seleccione un servicio',
        widget=forms.Select,
    )

    producto = ImagenChoiceField(
        queryset=Imagen.objects.all(),
        label='Producto (Opcional)',
        required=False,
        widget=forms.Select,
    )

    class Meta:
        model = Cita
        fields = ['servicio', 'producto', 'fecha', 'hora', 'comentario']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'comentario': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Comentarios adicionales…',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --------------------------
        # 1. WIDGET STYLES & CLASSES
        # --------------------------
        for field in self.fields.values():
            widget = field.widget
            base = 'form-select' if isinstance(widget, forms.Select) else 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {base}".strip()
            if not isinstance(widget, forms.Select):
                widget.attrs.setdefault('placeholder', field.label)

    # --------------------------
    # 2. PERSONALIZED VALIDATIONS
    # --------------------------
    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        # Asegura que comparamos fechas, no datetime
        fecha_date = fecha.date() if hasattr(fecha, 'date') else fecha
        # No reservar fines de semana
        if fecha_date.weekday() >= 5:
            raise forms.ValidationError("¡Puntalillo! Te recuerdo que el finde no curro.")
        # No reservar en pasado
        if fecha_date < timezone.now().date():
            raise forms.ValidationError("¡Ñooosss! ¡Se te fue el baifo! La fecha ya pasó.")
        return fecha_date

    def clean_hora(self):
        hora_str = self.cleaned_data['hora']
        hora_obj = datetime.strptime(hora_str, '%H:%M').time()
        if hora_obj < time(9, 30) or hora_obj > time(19, 30):
            raise forms.ValidationError("¡Se te fue el baifo! La hora está fuera del rango.")
        return hora_str

# Autor: José Félix Gordo Castaño
# Licencia: uso educativo, no comercial
