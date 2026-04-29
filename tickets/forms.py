from django import forms

from .models import Ticket


TITULO_MAX_LENGTH = 50
DESCRIPCION_MAX_LENGTH = 120


class TicketForm(forms.ModelForm):
    titulo = forms.CharField(
        label="Título",
        max_length=TITULO_MAX_LENGTH,
        min_length=5,
        widget=forms.TextInput(
            attrs={
                "maxlength": TITULO_MAX_LENGTH,
                "data-character-limit": TITULO_MAX_LENGTH,
            }
        ),
    )
    descripcion = forms.CharField(
        label="Descripción",
        max_length=DESCRIPCION_MAX_LENGTH,
        min_length=10,
        widget=forms.Textarea(
            attrs={
                "maxlength": DESCRIPCION_MAX_LENGTH,
                "data-character-limit": DESCRIPCION_MAX_LENGTH,
            }
        ),
    )

    class Meta:
        model = Ticket
        fields = ["titulo", "descripcion", "categoria", "prioridad"]

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if len(titulo) < 5:
            raise forms.ValidationError("El título debe tener al menos 5 caracteres.")
        if len(titulo) > TITULO_MAX_LENGTH:
            raise forms.ValidationError(f"El título no puede superar {TITULO_MAX_LENGTH} caracteres.")
        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data["descripcion"].strip()
        if len(descripcion) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres.")
        if len(descripcion) > DESCRIPCION_MAX_LENGTH:
            raise forms.ValidationError(f"La descripción no puede superar {DESCRIPCION_MAX_LENGTH} caracteres.")
        return descripcion
