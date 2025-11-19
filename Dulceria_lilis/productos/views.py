# productos/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.db.models import Q
from sistema.decorators import permiso_requerido
from .models import Producto
from .forms import ProductoForm
from utils.export_excel import queryset_to_excel

# ------------------------------
# LISTAR PRODUCTOS (con buscar y exportar)
# ------------------------------
@method_decorator(permiso_requerido('productos.view_producto'), name='dispatch')
class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'productos'
    ordering = ['nombre']

    def get_queryset(self):
        buscar = self.request.GET.get("buscar")
        if buscar is None:
            buscar = self.request.session.get('f_buscar', '')
        else:
            self.request.session["f_buscar"] = buscar
        qs = Producto.objects.all().order_by('nombre')
        if buscar:
            qs = qs.filter(Q(sku__icontains=buscar) | Q(nombre__icontains=buscar))
        return qs
    

    def get(self, request, *args, **kwargs):
        if request.GET.get("export") == "xlsx":
            qs = self.get_queryset()
            columns = [
                ("SKU", lambda p: p.sku),
                ("Nombre", lambda p: p.nombre),
                ("Categoría", lambda p: p.categoria),
                ("Marca", lambda p: p.marca or ""),
                ("Modelo", lambda p: p.modelo or ""),
                ("UOM Compra", lambda p: p.uom_compra),
                ("UOM Venta", lambda p: p.uom_venta),
                ("Factor conversión", lambda p: p.factor_conversion),
                ("Costo estándar", lambda p: float(p.costo_estandar) if p.costo_estandar else ""),
                ("Precio venta", lambda p: float(p.precio_venta) if p.precio_venta else ""),
                ("IVA %", lambda p: float(p.impuesto_iva) if p.impuesto_iva else ""),
                ("Stock actual", lambda p: p.stock_actual),
                ("Stock mínimo", lambda p: p.stock_minimo),
                ("Stock máximo", lambda p: p.stock_maximo or ""),
                ("Punto de reorden", lambda p: p.punto_reorden or ""),
                ("Perecible", lambda p: "Sí" if p.perishable else "No"),
                ("Control por lote", lambda p: "Sí" if p.control_por_lote else "No"),
                ("Control por serie", lambda p: "Sí" if p.control_por_serie else "No"),
                ("Imagen URL", lambda p: p.imagen_url or ""),
                ("Ficha técnica URL", lambda p: p.ficha_tecnica_url or ""),
            ]
            raw, fname = queryset_to_excel("productos", columns, qs)
            resp = HttpResponse(
                raw,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            resp["Content-Disposition"] = f'attachment; filename="{fname}"'
            return resp

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['buscar'] = self.request.session.get('f_buscar', '')
        ctx['busqueda_activa'] = bool(self.request.session.get('f_buscar', ''))
        ctx['form'] = ProductoForm()  # Formulario embebido
        return ctx

# ------------------------------
# CREAR PRODUCTO (POST desde lista)
# ------------------------------
@method_decorator(permiso_requerido('productos.add_producto'), name='dispatch')
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    success_url = reverse_lazy('productos:lista')

    def form_valid(self, form):
        sku = form.cleaned_data.get('sku')
        ean = form.cleaned_data.get('ean_upc')

        if Producto.objects.filter(sku=sku).exists():
            form.add_error('sku', 'Ya existe un producto con este SKU.')
            return self.form_invalid(form)

        if ean and Producto.objects.filter(ean_upc=ean).exists():
            form.add_error('ean_upc', 'Ya existe un producto con este EAN/UPC.')
            return self.form_invalid(form)

        producto = form.save(commit=False)
        producto.stock_actual = 0
        producto.costo_promedio = 0
        producto.save()

        messages.success(self.request, f"Producto '{producto.nombre}' creado correctamente.")

        f_buscar = self.request.session.get('f_buscar', '')
        if f_buscar:
            return redirect(f"{self.success_url}?q={f_buscar}")

        return redirect(self.success_url)

    def form_invalid(self, form):
        productos = Producto.objects.all().order_by('nombre')
        messages.error(self.request, "Por favor complete todos los campos obligatorios correctamente.")
        return render(self.request, 'productos/lista.html', {
            'productos': productos,
            'form': form,
        })


# ------------------------------
# EDITAR PRODUCTO
# ------------------------------
@method_decorator(permiso_requerido('productos.change_producto'), name='dispatch')
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/form.html'
    success_url = reverse_lazy('productos:lista')

    def form_valid(self, form):
        producto = form.save(commit=False)
        producto.save()
        messages.success(self.request, f"Producto '{producto.nombre}' actualizado correctamente.")
        f_q = self.request.session.get('f_q', '')
        if f_q:
            return redirect(f"{self.success_url}?q={f_q}")
        return super().form_valid(form)


# ------------------------------
# ELIMINAR PRODUCTO
# ------------------------------
@method_decorator(permiso_requerido('productos.delete_producto'), name='dispatch')
class ProductoDeleteView(DeleteView):
    model = Producto
    success_url = reverse_lazy('productos:lista')

    def get(self, request, *args, **kwargs):
        producto = get_object_or_404(Producto, pk=kwargs['pk'])
        producto.delete()
        messages.success(request, f"Producto '{producto.nombre}' eliminado correctamente.")
        return redirect(self.success_url)

# ------------------------------
# DETALLE DE PRODUCTO
# ------------------------------
@method_decorator(permiso_requerido('productos.view_producto'), name='dispatch')
class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/detalle.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['alerta_bajo_stock'] = self.object.alerta_bajo_stock()
        return ctx
