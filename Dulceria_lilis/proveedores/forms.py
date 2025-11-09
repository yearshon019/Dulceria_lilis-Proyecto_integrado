from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re
from .models import Proveedor, ProductoProveedor

# Validación personalizada para la URL del sitio web
def validar_sitio_web(value):
    # Si el campo no está vacío, validar si la URL tiene esquema (http:// o https://)
    if value:
        parsed_url = urlparse(value)
        # Extraer el dominio de la URL (el nombre que está antes del primer "/")
        domain = parsed_url.netloc or parsed_url.path  # Si no hay netloc, usamos el path
        
        if not parsed_url.scheme:
            # Si no tiene esquema (http:// o https://), mostrar el mensaje de error con el dominio
            raise ValidationError(
                f'La URL está mal escrita. Debe incluir el esquema como "http://{domain}.cl" en lugar de "{domain}".'
            )

# Opciones para las condiciones de pago
CONDICIONES_PAGO_CHOICES = [
    ('EFECTIVO', 'EFECTIVO'),
    ('DEBITO', 'DEBITO'),
    ('TRANSFERENCIA', 'TRANSFERENCIA'),
]

# Opciones para la moneda
MONEDA_CHOICES = [
    ('CLP', 'CLP'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
]

class ProveedorForm(forms.ModelForm):
    # Usamos CharField para el sitio web y le agregamos un validador personalizado
    sitio_web = forms.CharField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
        validators=[validar_sitio_web]  # Validación personalizada
    )
    
    condiciones_pago = forms.ChoiceField(
        choices=CONDICIONES_PAGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Seleccione una condición de pago válida.'}
    )

    moneda = forms.ChoiceField(
        choices=MONEDA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Seleccione una moneda válida.'}
    )

    class Meta:
        model = Proveedor
        fields = '__all__'
        widgets = {
            'rut_nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nombre_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'contacto_principal_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'contacto_principal_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'contacto_principal_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campo opcional'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Campo opcional'}),
        }
        error_messages = {
            'rut_nif': {'required': 'Ingrese el RUT del proveedor.'},
            'razon_social': {'required': 'Ingrese la razón social del proveedor.'},
            'email': {'required': 'Ingrese el email del proveedor.'},
            'condiciones_pago': {'required': 'Seleccione una condición de pago válida.'},
        }

        # Validación de email
    def clean_email(self):
        email = self.cleaned_data['email']
        if '@' not in email:
            raise ValidationError("El email debe contener un '@'.")
        if '.' not in email:
            raise ValidationError("El email debe contener un '.'.")
        if email.count('@') > 1:
            raise ValidationError("El email debe contener solo un '@'.")
        if email.count('.') > 1:
            raise ValidationError("El email debe contener solo un '.'.")
        if email.endswith('@'):
            raise ValidationError("El email debe contener un dominio.")
        return email
    
    # Validación de RUT
    def clean_rut_nif(self):
        rut = self.cleaned_data['rut_nif'].upper().replace('.', '').replace('-', '')  # Limpieza del RUT
        if not re.match(r'^\d{7,8}[0-9K]$', rut):  # Validación de formato
            raise ValidationError("Formato de RUT inválido. Ejemplo válido: 21983048-3")

        cuerpo, dv = rut[:-1], rut[-1]
        suma, multiplo = 0, 2
        for c in reversed(cuerpo):
            suma += int(c) * multiplo
            multiplo = multiplo + 1 if multiplo < 7 else 2
        resto = suma % 11
        calc = 11 - resto
        dv_esperado = '0' if calc == 11 else ('K' if calc == 10 else str(calc))

        if dv != dv_esperado:
            raise ValidationError("RUT inválido. El dígito verificador no coincide.")
        
        # Asegurarse de que no sea un RUT de prueba
        if rut == "111111111":  # RUT no válido
            raise ValidationError("El RUT '11111111-1' no es válido.")
        
        return f"{cuerpo}-{dv}"




    # Validación de teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
    
        if not telefono:
            return telefono  # Si el teléfono está vacío, lo dejamos pasar.
    
        if not telefono.isdigit():
            raise ValidationError("El teléfono debe contener solo números.")
    
        if len(telefono) != 9:
            raise ValidationError("El teléfono debe tener exactamente 9 dígitos.")
    
        if re.match(r'^(\d)\1{8,}$', telefono):
            raise ValidationError(f"El teléfono no debe contener secuencias repetidas como {telefono[0] * 9}.")
    
        return telefono


# Formulario para el modelo ProductoProveedor
class ProductoProveedorInlineForm(forms.ModelForm):
    class Meta:
        model = ProductoProveedor
        fields = ["producto", "costo", "preferente"]
        widgets = {
            "producto":   forms.Select(attrs={"class": "form-select"}),
            "costo":      forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Ej: 1500.00"}),
            "preferente": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

ProductoProveedorFormSet = forms.inlineformset_factory(
    Proveedor,
    ProductoProveedor,
    form=ProductoProveedorInlineForm,
    extra=1,
    can_delete=True,
)
