from django.forms import ValidationError
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views import View
from django.http import HttpResponse, JsonResponse
from proveedores.models import ProductoProveedor
from sistema.decorators import permiso_requerido
from .models import MovimientoInventario, Bodega, Lote
from .forms import MovimientoInventarioForm
from utils.export_excel import queryset_to_excel


# ----------------------------------------------------------
# LISTAR + CREAR EN LA MISMA PÁGINA (CON FILTROS, PAGINACIÓN Y EXPORTAR)
# ----------------------------------------------------------
@method_decorator(permiso_requerido('inventario.ver_movimientos'), name='dispatch')
@method_decorator(permiso_requerido('inventario.agregar_movimientos'), name='post')
class MovimientoInventarioListCreateView(View):
    template_name = 'inventario/movimiento_list.html'

    def _apply_filters(self, request, qs):
        tipo = (request.GET.get('tipo') or '').strip()
        producto = (request.GET.get('producto') or '').strip()
        bodega = (request.GET.get('bodega') or '').strip()

        if tipo:
            qs = qs.filter(tipo=tipo)
        if producto:
            qs = qs.filter(producto__nombre__icontains=producto)
        if bodega:
            tokens = [t.strip() for t in bodega.replace(';', ',').split(',') if t.strip()]
            q_obj = Q()
            for t in tokens:
                q_obj |= Q(bodega_origen__codigo__icontains=t)
                q_obj |= Q(bodega_origen__nombre__icontains=t)
                q_obj |= Q(bodega_destino__codigo__icontains=t)
                q_obj |= Q(bodega_destino__nombre__icontains=t)
            qs = qs.filter(q_obj)

        return qs, tipo, producto, bodega

    def get(self, request):
        movimientos = MovimientoInventario.objects.select_related(
            'producto', 'bodega_origen', 'bodega_destino', 'usuario'
        ).order_by('-fecha')

        # ===== EXPORTAR EXCEL =====
        if request.GET.get("export") == "xlsx":
            columns = [
                ("Fecha",           lambda m: m.fecha.replace(tzinfo=None) if m.fecha else ""),
                ("Tipo",            lambda m: m.tipo),
                ("Producto",        lambda m: m.producto.nombre if m.producto else ""),
                ("Cantidad",        lambda m: m.cantidad),
                ("Bodega Origen",   lambda m: str(m.bodega_origen) if m.bodega_origen else ""),
                ("Bodega Destino",  lambda m: str(m.bodega_destino) if m.bodega_destino else ""),
                ("Documento Ref.",  lambda m: m.documento_referencia or ""),
                ("Serie",           lambda m: m.serie or ""),
                ("Lote",            lambda m: str(m.lote) if m.lote else ""),
                ("Observación",     lambda m: m.observacion or ""),
                ("Usuario",         lambda m: m.usuario.username if m.usuario_id else ""),
            ]
            raw, fname = queryset_to_excel("movimientos_inventario", columns, movimientos)
            resp = HttpResponse(
                raw,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            resp["Content-Disposition"] = f'attachment; filename="{fname}"'
            return resp

        # ===== FILTROS =====
        movimientos, tipo, producto, bodega = self._apply_filters(request, movimientos)

        # ===== PAGINADOR =====
        try:
            per_page = int(request.GET.get('pp') or 5)
        except ValueError:
            per_page = 5
        if per_page not in (5, 10, 20):
            per_page = 5

        paginator = Paginator(movimientos, per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if request.method == "POST":
            form = MovimientoInventarioForm(request.POST)
        else:
            form = MovimientoInventarioForm(initial=request.GET)




        context = {
            'form': form,
            'page_obj': page_obj,
            'movimientos': page_obj,
            'bodegas': Bodega.objects.all(),
            'f_tipo': tipo,
            'f_producto': producto,
            'f_bodega': bodega,
            'per_page': per_page,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            if request.user.is_authenticated:
                movimiento.usuario = request.user
            try:
                movimiento.save()
                messages.success(request, "✅ Movimiento registrado correctamente.")
                return redirect('inventario:inicio')

            except ValidationError as e:
                # Manda el error al formulario
                form.add_error(None, e.message)
                # Manda el error como alerta
                messages.error(request, f"❌ {e.message}")
        if form.errors:
            messages.error(request, "⚠️ Por favor complete todos los campos obligatorios correctamente.")

        movimientos = MovimientoInventario.objects.select_related(
            'producto', 'bodega_origen', 'bodega_destino', 'usuario'
        ).order_by('-fecha')
        
        movimientos, tipo, producto, bodega = self._apply_filters(request, movimientos)
        
        try:
            per_page = int(request.GET.get('pp') or 5)
        except ValueError:
            per_page = 5
        if per_page not in (5, 10, 20):
            per_page = 5
            
        paginator = Paginator(movimientos, per_page)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'form': form,
            'page_obj': page_obj,
            'movimientos': page_obj,
            'bodegas': Bodega.objects.all(),
            'f_tipo': tipo,
            'f_producto': producto,
            'f_bodega': bodega,
            'per_page': per_page,
        }
        return render(request, self.template_name, context)
def productos_por_proveedor(request, proveedor_id):
    productos = ProductoProveedor.objects.filter(
        proveedor_id=proveedor_id
    ).select_related("producto")

    data = [
        {"id": pp.producto.id,
         "nombre": pp.producto.nombre,
         "sku": pp.producto.sku if hasattr(pp.producto, "sku") else "",
         }
         for pp in productos
    ]

    return JsonResponse({"productos": data})
def lotes_por_producto(request, producto_id):
    """
    Devuelve los lotes disponibles para un producto (solo stock > 0)
    Se usa por AJAX cuando el usuario selecciona un producto.
    """
    lotes = Lote.objects.filter(
        producto_id=producto_id,
        cantidad_disponible__gt=0
    ).order_by('codigo')

    data = [
        {
            "id": lote.id,
            "codigo": lote.codigo,
            "descripcion": str(lote),
            "disponible": float(lote.cantidad_disponible),
        }
        for lote in lotes
    ]

    return JsonResponse({"lotes": data})



# ----------------------------------------------------------
# DETALLE DE MOVIMIENTO
# ----------------------------------------------------------
@method_decorator(permiso_requerido('inventario.ver_movimientos'), name='dispatch')
class MovimientoInventarioDetailView(DetailView):
    model = MovimientoInventario
    template_name = 'inventario/movimiento_detalle.html'
    context_object_name = 'movimiento'


# ----------------------------------------------------------
# EDITAR MOVIMIENTO
# ----------------------------------------------------------
@method_decorator(permiso_requerido('inventario.editar_movimientos'), name='dispatch')
class MovimientoInventarioUpdateView(UpdateView):
    model = MovimientoInventario
    form_class = MovimientoInventarioForm
    template_name = 'inventario/movimiento_form.html'
    success_url = reverse_lazy('inventario:inicio')

    def form_valid(self, form):
        messages.success(self.request, "✅ Movimiento actualizado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "⚠️ Revisa los errores del formulario.")
        return super().form_invalid(form)


# ----------------------------------------------------------
# LISTAR BODEGAS
# ----------------------------------------------------------
@method_decorator(permiso_requerido('inventario.ver_bodegas'), name='dispatch')
class BodegaListView(ListView):
    model = Bodega
    template_name = 'inventario/bodega_list.html'
    context_object_name = 'bodegas'
    ordering = ['codigo']
