from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Reporte

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    email = forms.EmailField(label="Correo")

    class Meta:
        model = User
        fields = ["first_name", "email"]

    def clean_email(self):
        correo = self.cleaned_data["email"].lower()
        if User.objects.filter(username=correo).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return correo

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data["email"]
        if commit:
            usuario.save()
        return usuario
class IngresoForm(AuthenticationForm):
    username = forms.CharField(label="Correo")

    error_messages = {
        "invalid_login": "El correo o la contraseña no son correctos.",
        "inactive": "Esta cuenta está desactivada.",
    }

    def clean_username(self):
        return self.cleaned_data["username"].lower()
class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ["estado", "detalle", "referencia"]
        labels = {
            "detalle": "Detalle (opcional)",
            "referencia": "¿Dónde estás?",
        }
        widgets = {
            "detalle": forms.TextInput(attrs={"placeholder": "Ej: estoy sin batería"}),
            "referencia": forms.TextInput(attrs={"placeholder": "Ej: en la casa, en la U"}),
        }