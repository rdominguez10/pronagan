from django import forms
from django.contrib.auth.forms import AuthenticationForm
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class RegistroUsuarioForm(forms.Form):
    usuario = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Usuario'}),
            error_messages={
            'required': 'Este campo es obligatorio',
        })
    
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Contraseña'}),
            error_messages={
            'required': 'Este campo es obligatorio',
        })
    
    rep_contrasena = forms.CharField(
        label="Repetir Contraseña",
        widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Repetir Contraseña'}),
                error_messages={
            'required': 'Este campo es obligatorio',
        })
    
    nombre = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nombre'}),
        error_messages={
            'required': 'Este campo es obligatorio',
        })
    
    apellidos = forms.CharField(
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Apellidos'}),
                    error_messages={
            'required': 'Este campo es obligatorio',
        })
