from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario
from django.core.exceptions import ValidationError
import re

# =====================
# LOGIN FORM
# =====================
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o email'}),
        label="Usuario o email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label="Contraseña"
    )

# =====================
# USUARIO FORM
# =====================
class UsuarioForm(forms.ModelForm):
    ROL_CHOICES = [
        ('', 'Seleccione rol'),  # ← agrega esta línea para permitir opción vacía
        ('ADMIN', 'ADMIN'),
        ('PROVEEDOR', 'PROVEEDOR'),
        ('OPERADOR', 'OPERADOR'),
    ]

    ESTADO_CHOICES = [
        ('ACTIVO', 'ACTIVO'),
        ('BLOQUEADO', 'BLOQUEADO'),
        ('INACTIVO', 'INACTIVO'),
    ]

    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        required=False,  # ← evita el “This field is required.”
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'nombres', 'apellidos', 'telefono',
            'rol', 'estado', 'mfa_habilitado', 'area', 'observaciones'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'mfa_habilitado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        error_messages = {
            'username': {'required': 'Por favor, ingresa un nombre de usuario.'},
            'email': {'required': 'Por favor, ingresa una dirección de correo electrónica.'},
            'nombres': {'required': 'Por favor, ingresa tus nombres.'},
            'apellidos': {'required': 'Por favor, ingresa tus apellidos.'},
            'telefono': {'required': 'Por favor, ingresa un teléfono.'},
            'rol': {'required': 'Por favor, selecciona un rol.'},
            'estado': {'required': 'Por favor, selecciona un estado.'},
            'area': {'required': 'Por favor, ingresa el nombre de la area.'},
        }

    # =====================
    # VALIDACIONES PERSONALIZADAS
    # =====================
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Si está vacío → error inmediato
        if not email or not email.strip():
            raise forms.ValidationError("Por favor, ingresa una dirección de correo electrónica.")

        email = email.strip()

        # Validación de formato básico
        if '@' not in email:
            raise forms.ValidationError("Por favor, ingresa una dirección de correo electrónica válida.")

        # Validación de duplicado (excluyendo el usuario actual si se está editando)
        if Usuario.objects.filter(email__iexact=email).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")

        # Validación de regex (formato correcto)
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Por favor, ingresa una dirección de correo electrónica válida.")

        return email


    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono:
            raise forms.ValidationError("Por favor, ingresa un teléfono.")
        telefono = telefono.strip()

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono debe contener solo números.")
        if len(telefono) != 9:
            raise forms.ValidationError("El teléfono debe tener exactamente 9 dígitos.")
        if re.match(r'^(\d)\1{8,}$', telefono):
            raise forms.ValidationError(f"El teléfono no debe contener secuencias repetidas como {telefono[0] * 9}.")
        return telefono

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 20:
            raise forms.ValidationError("El nombre de usuario no puede exceder los 20 caracteres.")
        if username and not username.isalnum():
            raise forms.ValidationError("El nombre de usuario debe contener solo caracteres alfanuméricos.")
        return username

    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if not nombres or not nombres.strip():
            raise forms.ValidationError("Por favor, ingresa tu nombre.")
        if len(nombres) > 20:
            raise forms.ValidationError("El nombre no puede exceder los 20 caracteres.")
        if not nombres.isalpha():
            raise forms.ValidationError("El nombre debe contener solo letras.")
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if not apellidos or not apellidos.strip():
            raise forms.ValidationError("Por favor, ingresa tus apellidos.")
        if len(apellidos) > 40:
            raise forms.ValidationError("Los apellidos no pueden exceder los 40 caracteres.")
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s-]+$', apellidos):
            raise forms.ValidationError("Los apellidos deben contener solo letras.")
        return apellidos
    
    def clean_rol(self):
        rol = (self.cleaned_data.get('rol') or '').strip()
        if not rol:
            raise forms.ValidationError("Por favor, selecciona un rol.")
        return rol

    def clean_estado(self):
        estado = (self.cleaned_data.get('estado') or '').strip()
        if not estado:
            raise forms.ValidationError("Por favor, selecciona un estado.")
        return estado



# =====================
# PERFIL FORM
# =====================
MAX_AVATAR_MB = 2
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nombres", "apellidos", "email", "telefono", "avatar"]
        widgets = {
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = Usuario.objects.filter(email__iexact=email)
            if self.user:
                qs = qs.exclude(pk=self.user.pk)
            if qs.exists():
                raise ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean_avatar(self):
        file = self.cleaned_data.get("avatar")
        if not file:
            return file
        if file.size > MAX_AVATAR_MB * 1024 * 1024:
            raise ValidationError(f"El avatar excede {MAX_AVATAR_MB} MB.")
        ctype = getattr(file, "content_type", None)
        if ctype and ctype.lower() not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise ValidationError("Formato no permitido. Usa JPG, PNG o WEBP.")
        return file
    

