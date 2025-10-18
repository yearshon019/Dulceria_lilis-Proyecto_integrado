from django.db import models

class Producto(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    ean_upc = models.CharField(max_length=50, blank=True, null=True, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)

    uom_compra = models.CharField(max_length=20, default='UN')
    uom_venta = models.CharField(max_length=20, default='UN')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=4, default=1)
    costo_estandar = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    costo_promedio = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)  # solo lectura si calculas
    precio_venta = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19.0)

    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_maximo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    punto_reorden = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    perishable = models.BooleanField(default=False)
    control_por_lote = models.BooleanField(default=False)
    control_por_serie = models.BooleanField(default=False)

    imagen_url = models.URLField(blank=True, null=True)
    ficha_tecnica_url = models.URLField(blank=True, null=True)

    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def alerta_bajo_stock(self):
        return self.stock_actual <= (self.punto_reorden or self.stock_minimo)

    def __str__(self):
        return f"{self.sku} - {self.nombre}"