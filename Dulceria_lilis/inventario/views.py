from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django import forms
from .models import MovimientoInventario, Bodega, Lote
from productos.models import Producto
from proveedores.models import Proveedor


# ----------------------------------------------------------
# FORMULARIO DE MOVIMIENTO DE INVENTARIO
# ----------------------------------------------------------
class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = [
            'tipo', 'producto', 'proveedor', 'bodega_origen', 'bodega_destino',
            'cantidad', 'lote', 'serie', 'fecha_vencimiento',
            'observacion', 'documento_referencia'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'bodega_origen': forms.Select(attrs={'class': 'form-select'}),
            'bodega_destino': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documento_referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        cantidad = cleaned_data.get('cantidad')

        if cantidad and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que 0.")

        if tipo == 'TRANSFERENCIA':
            origen = cleaned_data.get('bodega_origen')
            destino = cleaned_data.get('bodega_destino')
            if not origen or not destino:
                raise forms.ValidationError("Debe indicar bodega origen y destino para una transferencia.")
        return cleaned_data


# ----------------------------------------------------------
# LISTAR MOVIMIENTOS DE INVENTARIO
# ----------------------------------------------------------
class MovimientoInventarioListView(ListView):
    model = MovimientoInventario
    template_name = 'inventario/movimiento_list.html'
    context_object_name = 'movimientos'
    ordering = ['-fecha']


# ----------------------------------------------------------
# CREAR MOVIMIENTO DE INVENTARIO
# ----------------------------------------------------------
class MovimientoInventarioCreateView(CreateView):
    model = MovimientoInventario
    form_class = MovimientoInventarioForm
    template_name = 'inventario/movimiento_form.html'
    success_url = reverse_lazy('inventario:inicio')

    def form_valid(self, form):
        # Guarda el usuario que realiza el movimiento si está autenticado
        if self.request.user.is_authenticated:
            form.instance.usuario = self.request.user
        return super().form_valid(form)


# ----------------------------------------------------------
# DETALLE DE MOVIMIENTO
# ----------------------------------------------------------
class MovimientoInventarioDetailView(DetailView):
    model = MovimientoInventario
    template_name = 'inventario/movimiento_detalle.html'
    context_object_name = 'movimiento'


# ----------------------------------------------------------
# LISTAR BODEGAS
# ----------------------------------------------------------
class BodegaListView(ListView):
    model = Bodega
    template_name = 'inventario/bodega_list.html'
    context_object_name = 'bodegas'
    ordering = ['codigo']
