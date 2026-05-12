from pathlib import Path

from django import forms
from django.contrib.staticfiles import finders

from .models import MensajeEspecial


def get_lottie_file_choices():
    choices = [("", "Sin animación")]
    lottie_dir = finders.find("lottie")

    if not lottie_dir:
        return choices

    lottie_path = Path(lottie_dir)
    if lottie_path.is_file():
        lottie_path = lottie_path.parent

    if not lottie_path.exists() or not lottie_path.is_dir():
        return choices

    for json_file in sorted(lottie_path.glob("*.json")):
        relative_path = f"lottie/{json_file.name}"
        choices.append((relative_path, json_file.name))

    return choices


class MensajeEspecialAdminForm(forms.ModelForm):
    lottie_file = forms.ChoiceField(required=False, choices=())

    class Meta:
        model = MensajeEspecial
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = get_lottie_file_choices()
        current_value = self.instance.lottie_file if self.instance.pk else self.initial.get("lottie_file", "")

        if current_value and current_value not in {value for value, _ in choices}:
            choices.append((current_value, Path(current_value).name))

        self.fields["lottie_file"].choices = choices
        self.fields["lottie_file"].help_text = "Selecciona un archivo de /static/lottie/"