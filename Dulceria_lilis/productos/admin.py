from django.contrib import admin
from .models import Producto

<<<<<<< HEAD
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("sku", "nombre", "categoria", "precio_venta", "stock_actual")
    search_fields = ("sku", "nombre", "categoria")  # 🔥 Necesario
=======
admin.site.register(Producto)
>>>>>>> 35238ce3c7b5ffbc00cce3e386f10ecdd91faba0
