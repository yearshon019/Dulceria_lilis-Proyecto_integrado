from django.db import models
from productos.models import Producto
from proveedores.models import Proveedor
from usuarios.models import Usuario

TIPO_MOVIMIENTO = [
    ('INGRESO', 'Ingreso'),
    ('SALIDA', 'Salida'),
    ('AJUSTE', 'Ajuste'),
    ('DEVOLUCION', 'Devolución'),
    ('TRANSFERENCIA', 'Transferencia'),
]

class Bodega(models.Model):
    nombre = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Lote(models.Model):
    codigo = models.CharField(max_length=120)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.codigo} - {self.producto}"

class MovimientoInventario(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    bodega_origen = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_origen')
    bodega_destino = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_destino')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True)
    serie = models.CharField(max_length=120, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} {self.producto} ({self.cantidad})"
