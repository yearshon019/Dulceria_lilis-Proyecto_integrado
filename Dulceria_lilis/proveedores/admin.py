from django.contrib import admin
<<<<<<< HEAD
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "email", "telefono", "ciudad", "estado")
    search_fields = ("razon_social", "email", "telefono", "ciudad")  # 🔥 Necesario
=======

# Register your models here.
from .models import Proveedor

admin.site.register(Proveedor)
>>>>>>> 35238ce3c7b5ffbc00cce3e386f10ecdd91faba0
