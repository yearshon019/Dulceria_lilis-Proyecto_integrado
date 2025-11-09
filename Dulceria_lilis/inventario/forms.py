from django import forms
from .models import MovimientoInventario

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
        error_messages = {
            'tipo': {'required': 'Por favor seleccione un tipo de movimiento.'},
            'producto': {'required': 'Por favor seleccione un producto.'},
            'proveedor': {'required': 'Por favor seleccione un proveedor.'},
            'cantidad': {'required': 'Ingrese la cantidad del movimiento.'},
            'bodega_origen': {'required': 'Seleccione la bodega de origen.'},
            'bodega_destino': {'required': 'Seleccione la bodega de destino.'},
            'lote': {'required': 'Seleccione un lote.'},
        }

    # Validación de cantidad
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return cantidad

    # Validaciones generales
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        origen = cleaned_data.get('bodega_origen')
        destino = cleaned_data.get('bodega_destino')
        producto = cleaned_data.get('producto')
        lote = cleaned_data.get('lote')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')

        # Validación para transferencias
        if tipo == 'TRANSFERENCIA':
            if not origen:
                self.add_error('bodega_origen', "Debe seleccionar una bodega de origen.")
            if not destino:
                self.add_error('bodega_destino', "Debe seleccionar una bodega de destino.")
            if origen == destino and origen is not None:
                self.add_error('bodega_destino', "La bodega destino no puede ser igual a la de origen.")

        # Validación de lote
        if lote and producto and lote.producto != producto:
            self.add_error('lote', "El lote seleccionado no corresponde al producto elegido.")

        # Fecha de vencimiento obligatoria si no hay lote
        if not fecha_vencimiento and not lote:
            self.add_error('fecha_vencimiento', "Debe indicar fecha de vencimiento o seleccionar un lote.")
            
        return cleaned_data
    
