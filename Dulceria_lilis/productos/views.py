from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django import forms
from .models import Producto
from sistema.decorators import permiso_requerido
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

# ----------------------------------------------------------
# FORMULARIO PERSONALIZADO PARA PRODUCTO
# ----------------------------------------------------------
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CHOCO-001'}),
            'ean_upc': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'uom_compra': forms.TextInput(attrs={'class': 'form-control'}),
            'uom_venta': forms.TextInput(attrs={'class': 'form-control'}),
            'factor_conversion': forms.NumberInput(attrs={'class': 'form-control'}),
            'costo_estandar': forms.NumberInput(attrs={'class': 'form-control'}),
            'costo_promedio': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'impuesto_iva': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'punto_reorden': forms.NumberInput(attrs={'class': 'form-control'}),
            'perishable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_lote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_serie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen_url': forms.URLInput(attrs={'class': 'form-control'}),
            'ficha_tecnica_url': forms.URLInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        }

    # Validación personalizada para precios
    def clean_precio_venta(self):
        precio = self.cleaned_data.get('precio_venta')
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio de venta no puede ser negativo.")
        return precio


# ----------------------------------------------------------
# LISTAR PRODUCTOS
# ----------------------------------------------------------
@method_decorator(permiso_requerido('productos.view_producto'), name='dispatch')
class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'productos'
    ordering = ['nombre']


# ----------------------------------------------------------
# CREAR PRODUCTO
# ----------------------------------------------------------


@method_decorator(permiso_requerido('productos.add_producto'), name='dispatch')
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/form.html'
    success_url = reverse_lazy('productos:lista')  

    def form_valid(self, form):
        sku = form.cleaned_data.get('sku')
        if Producto.objects.filter(sku=sku).exists():
            form.add_error('sku', 'Ya existe un producto con este SKU.')
            return self.form_invalid(form)
        return super().form_valid(form)


# ----------------------------------------------------------
# EDITAR PRODUCTO
# ----------------------------------------------------------
@method_decorator(permiso_requerido('productos.change_producto'), name='dispatch')
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/form.html'
    success_url = reverse_lazy('productos:lista')  


# ----------------------------------------------------------
# ELIMINAR PRODUCTO
# ----------------------------------------------------------
@method_decorator(permiso_requerido('productos.delete_producto'), name='dispatch')
class ProductoDeleteView(DeleteView):
    model = Producto
    success_url = reverse_lazy('productos:lista')
    def get(self, request, *args, **kwargs):
        producto = get_object_or_404(Producto, pk=kwargs['pk'])
        producto.delete()
        messages.success(request, f"Producto '{producto.nombre}' eliminado correctamente.")
        return redirect(self.success_url)



# ----------------------------------------------------------
# DETALLE DE PRODUCTO
# ----------------------------------------------------------
@method_decorator(permiso_requerido('productos.view_producto'), name='dispatch')
class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calcular alerta de bajo stock
        context['alerta_bajo_stock'] = self.object.alerta_bajo_stock()
        return context
