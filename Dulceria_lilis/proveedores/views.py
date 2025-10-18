from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Proveedor, ProductoProveedor
from django import forms
from django.shortcuts import render
import re
from django.core.exceptions import ValidationError



# ----------------------------------------------------------
# FORMULARIO PERSONALIZADO PARA PROVEEDOR
# ----------------------------------------------------------
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'
        widgets = {
            'rut_nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'condiciones_pago': forms.TextInput(attrs={'class': 'form-control'}),
            'moneda': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_principal_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_principal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contacto_principal_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # Validación personalizada
    def clean_rut_nif(self):
        rut = self.cleaned_data['rut_nif'].upper().replace('.', '').replace('-', '')

        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            raise ValidationError("Formato de RUT inválido. Ejemplo válido: 21983048-3")

        cuerpo = rut[:-1]
        dv = rut[-1]

        suma = 0
        multiplo = 2

        for c in reversed(cuerpo):
            suma += int(c) * multiplo
            multiplo = multiplo + 1 if multiplo < 7 else 2

        resto = suma % 11
        dv_calculado = 11 - resto

        if dv_calculado == 11:
            dv_esperado = '0'
        elif dv_calculado == 10:
            dv_esperado = 'K'
        else:
            dv_esperado = str(dv_calculado)

        if dv != dv_esperado:
            raise ValidationError("RUT inválido. El dígito verificador no coincide.")
        return f"{cuerpo}-{dv}"

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not telefono:
            raise ValidationError("El teléfono es obligatorio.")
        if not telefono.isdigit():
            raise ValidationError("El teléfono debe contener solo números.")
        if len(telefono) != 9:
            raise ValidationError("El teléfono debe tener exactamente 9 dígitos.")
        return telefono



# ----------------------------------------------------------
# LISTAR PROVEEDORES
# ----------------------------------------------------------
class ProveedorListView(ListView):
    model = Proveedor
    template_name = 'proveedores/lista_proveedor.html'
    context_object_name = 'proveedores'
    ordering = ['razon_social']


# ----------------------------------------------------------
# CREAR PROVEEDOR
# ----------------------------------------------------------
class ProveedorCreateView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/form_proveedor.html'
    success_url = reverse_lazy('proveedores:lista')

    def form_valid(self, form):
        # Si el email ya existe, prevenir duplicados
        email = form.cleaned_data.get('email')
        if Proveedor.objects.filter(email=email).exists():
            form.add_error('email', 'Ya existe un proveedor con este correo electrónico.')
            return self.form_invalid(form)
        return super().form_valid(form)


# ----------------------------------------------------------
# EDITAR PROVEEDOR
# ----------------------------------------------------------
class ProveedorUpdateView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/form_proveedor.html'
    success_url = reverse_lazy('proveedores:lista')


# ----------------------------------------------------------
# ELIMINAR PROVEEDOR
# ----------------------------------------------------------
class ProveedorDeleteView(DeleteView):
    model = Proveedor
    template_name = 'proveedores/confirm_delete_proveedor.html'
    success_url = reverse_lazy('proveedores:lista')


# ----------------------------------------------------------
# DETALLE DE PROVEEDOR
# ----------------------------------------------------------
class ProveedorDetailView(DetailView):
    model = Proveedor
    template_name = 'proveedores/detalle_proveedor.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los productos asociados al proveedor en el detalle.
        """
        context = super().get_context_data(**kwargs)
        context['productos_asociados'] = ProductoProveedor.objects.filter(proveedor=self.object)
        return context
