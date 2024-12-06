# reviews/forms.py
from django import forms
from .models import Resena


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['servicio', 'texto', 'puntuacion']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'puntuacion': forms.RadioSelect(attrs={'class': 'rating'}),
        }
