from django.contrib import admin
<<<<<<< HEAD
from .models import MovimientoInventario, Bodega, Lote


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "ubicacion")
    search_fields = ("codigo", "nombre", "ubicacion")


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("codigo", "producto", "fecha_vencimiento")
    search_fields = ("codigo", "producto__nombre")
    list_filter = ("fecha_vencimiento", "producto")


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("fecha", "tipo", "producto", "cantidad", "bodega_origen", "bodega_destino", "usuario")
    list_filter = ("tipo", "fecha")

    # 🔥 ESTA LÍNEA ES LA CLAVE (antes no se reconocía correctamente)
    search_fields = ("producto__nombre", "tipo", "documento_referencia", "observacion")

    # Campos que se completan automáticamente con búsqueda
    autocomplete_fields = ("producto", "proveedor", "bodega_origen", "bodega_destino", "lote")
=======

# Register your models here.
from .models import MovimientoInventario

admin.site.register(MovimientoInventario)
>>>>>>> 35238ce3c7b5ffbc00cce3e386f10ecdd91faba0
