# appointments/forms.py
from django import forms
from datetime import datetime
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
        raw_fecha = self.cleaned_data["fecha"]

        # 🔑  SI viene datetime → conviértelo a date
        fecha = raw_fecha.date() if isinstance(raw_fecha, datetime) else raw_fecha

        if fecha.weekday() >= 5:
            raise forms.ValidationError("¡El finde no curro!")
        if fecha < timezone.localdate():        # hoy (aware)
            raise forms.ValidationError("La fecha ya pasó.")
        return fecha   

# Autor: José Félix Gordo Castaño
# Licencia: uso educativo, no comercial
