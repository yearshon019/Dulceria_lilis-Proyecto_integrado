from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MovimientoInventario
from productos.models import Producto

@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock(sender, instance, created, **kwargs):
    if not created:
        return
    prod = instance.producto
    if instance.tipo == 'INGRESO':
        prod.stock_actual = (prod.stock_actual or 0) + instance.cantidad
    elif instance.tipo in ('SALIDA', 'DEVOLUCION'):
        prod.stock_actual = (prod.stock_actual or 0) - instance.cantidad
    # AJUSTE podría ser positivo o negativo según observación o campo adicional
    prod.save()
