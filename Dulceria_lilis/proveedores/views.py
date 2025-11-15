# proveedores/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.db.models import Q
from .models import Proveedor, ProductoProveedor, Producto
from .forms import ProveedorForm, ProductoProveedorFormSet, ProductoRelacionForm
from sistema.decorators import permiso_requerido
from utils.export_excel import queryset_to_excel


# ----------------------------------------------------------
# LISTAR PROVEEDORES + CREAR EN LA MISMA PÁGINA
# ----------------------------------------------------------
class ProveedorListView(ListView):
    model = Proveedor
    template_name = 'proveedores/lista_proveedor.html'
    context_object_name = 'proveedores'
    ordering = ['razon_social']

    def get_queryset(self):
        buscar_Rut_Nif = self.request.GET.get("buscar_Rut_Nif")
        if buscar_Rut_Nif is None:
            buscar_Rut_Nif = self.request.session.get('f_buscar_Rut_Nif', '')
        else:
            self.request.session["f_buscar_Rut_Nif"] = buscar_Rut_Nif
        qs = Proveedor.objects.all().order_by('rut_nif', 'razon_social')
        if buscar_Rut_Nif:
            qs = qs.filter(Q(rut_nif__icontains=buscar_Rut_Nif) | Q(razon_social__icontains=buscar_Rut_Nif))
        return qs

    def get(self, request, *args, **kwargs):
        # Exportar a Excel si se solicita
        if request.GET.get("export") == "xlsx":
            qs = self.get_queryset()
            columns = [
                ("RUT/NIF", lambda pr: pr.rut_nif),
                ("Razón social", lambda pr: pr.razon_social),
                ("Nombre fantasía", lambda pr: pr.nombre_fantasia or ""),
                ("Email", lambda pr: pr.email),
                ("Teléfono", lambda pr: pr.telefono or ""),
                ("Ciudad", lambda pr: pr.ciudad or ""),
                ("País", lambda pr: pr.pais),
                ("Condiciones de pago", lambda pr: pr.condiciones_pago),
                ("Moneda", lambda pr: pr.moneda),
                ("Contacto principal", lambda pr: pr.contacto_principal_nombre or ""),
                ("Estado", lambda pr: pr.estado),
            ]
            raw, fname = queryset_to_excel("proveedores", columns, qs)
            resp = HttpResponse(
                raw,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            resp["Content-Disposition"] = f'attachment; filename="{fname}"'
            return resp

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Formulario principal
        if "form" not in ctx:
            ctx["form"] = ProveedorForm()

        # 🔹 Enviar listado de productos para el select
        ctx["productos"] = Producto.objects.all().order_by("nombre")

        # 🔹 Enviar filtros para mantenerlos al recargar
        ctx["buscar_Rut_Nif"] = self.request.session.get('f_buscar_Rut_Nif', '')

        # 🔹 Enviar formset vacío para usar en el HTML
        ctx["pp_formset"] = ProductoProveedorFormSet()

        # Si viene desde POST, úsalo. Si no, crea uno vacío.
        if "rel_form" not in ctx:
            ctx["rel_form"] = ProductoRelacionForm()

        ctx["titulo"] = "Registrar proveedor"
        return ctx

    def post(self, request, *args, **kwargs):
        form = ProveedorForm(request.POST)
        rel_form = ProductoRelacionForm(request.POST)

        # ---------- VALIDACIÓN DEL FORM PRINCIPAL ----------
        if form.is_valid():
            rut = form.cleaned_data.get('rut_nif')
            email = form.cleaned_data.get('email')

            if Proveedor.objects.filter(rut_nif=rut).exists():
                form.add_error('rut_nif', 'Ya existe un proveedor con este RUT/NIF.')

            if Proveedor.objects.filter(email=email).exists():
                form.add_error('email', 'Ya existe un proveedor con este correo electrónico.')

        # Si hubo errores → recargar
        if form.errors:
            messages.error(request, 'Por favor complete todos los campos obligatorios correctamente.')
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context["form"] = form
            context["rel_form"] = rel_form  # ⭐ AGREGADO
            return self.render_to_response(context)

        # ======================================================
        # VALIDAR TAB 3 CON EL FORM ProductoRelacionForm
        # ======================================================
        if not rel_form.is_valid():
            messages.error(request, "Corrige los errores del TAB 3.")
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context["form"] = form
            context["rel_form"] = rel_form  # ⭐ AGREGADO
            return self.render_to_response(context)

        # ======================================================
        # GUARDAR PROVEEDOR
        # ======================================================
        proveedor = form.save()

        # ======================================================
        # GUARDAR TAB 3 (solo si eligieron producto)
        # ======================================================
        producto = rel_form.cleaned_data.get("producto_rel")

        if producto:
            ProductoProveedor.objects.create(
                proveedor=proveedor,
                producto=producto,
                costo=rel_form.cleaned_data.get("costo_rel"),
                lead_time_dias=rel_form.cleaned_data.get("lead_time_rel"),
                min_lote=rel_form.cleaned_data.get("min_lote_rel"),
                descuento_pct=rel_form.cleaned_data.get("descuento_rel") or 0,
                preferente=rel_form.cleaned_data.get("preferente_rel") or False,
            )

        messages.success(request, 'Proveedor creado correctamente.')
        return redirect('proveedores:lista')


# ----------------------------------------------------------
# CREAR PROVEEDOR EN RUTA APARTE (Opcional)
# ----------------------------------------------------------
class ProveedorCreateView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    success_url = reverse_lazy('proveedores:lista')

    def form_valid(self, form):
        rut = form.cleaned_data.get('rut_nif')
        email = form.cleaned_data.get('email')
        if Proveedor.objects.filter(rut_nif=rut).exists():
            form.add_error('rut_nif', 'Ya existe un proveedor con este RUT/NIF.')
            return self.form_invalid(form)
        if Proveedor.objects.filter(email=email).exists():
            form.add_error('email', 'Ya existe un proveedor con este correo electrónico.')
            return self.form_invalid(form)

        self.object = form.save()
        messages.success(self.request, "Proveedor creado correctamente.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        proveedores = Proveedor.objects.all().order_by('razon_social')
        context = {'proveedores': proveedores, 'form': form, 'titulo': 'Registrar proveedor'}
        return render(self.request, 'proveedores/lista_proveedor.html', context)



# ----------------------------------------------------------
# EDITAR PROVEEDOR
# ----------------------------------------------------------
class ProveedorUpdateView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/form_proveedor.html'
    success_url = reverse_lazy('proveedores:lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # FORMSET: Carga y edición de productos asociados
        if self.request.POST:
            context["pp_formset"] = ProductoProveedorFormSet(self.request.POST, instance=self.object)
        else:
            context["pp_formset"] = ProductoProveedorFormSet(instance=self.object)

        # Productos para el select
        context["productos"] = Producto.objects.all()

        context['titulo'] = 'Editar'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pp_formset = context["pp_formset"]

        if pp_formset.is_valid():

            # Guardar el proveedor
            self.object = form.save()

            # Guardar cambios del formset (edición y eliminación)
            pp_formset.instance = self.object
            pp_formset.save()

            # --- AGREGAR NUEVA RELACIÓN ---
            prod_id = self.request.POST.get("producto_rel")

            if prod_id:
                producto = Producto.objects.get(pk=prod_id)

                # Prevenir duplicados
                ya_existe = ProductoProveedor.objects.filter(
                    proveedor=self.object,
                    producto=producto
                ).exists()

                if not ya_existe:
                    ProductoProveedor.objects.create(
                        proveedor=self.object,
                        producto=producto,
                        costo=self.request.POST.get("costo_rel") or 0,
                        lead_time_dias=self.request.POST.get("lead_time_rel") or 7,
                        min_lote=self.request.POST.get("min_lote_rel") or 1,
                        descuento_pct=self.request.POST.get("descuento_rel") or 0,
                        preferente=True if self.request.POST.get("preferente_rel") == "on" else False,
                    )

            # 🔥 SIEMPRE REDIRIGIR DESPUÉS DE GUARDAR
            messages.success(self.request, "Cambios guardados correctamente.")
            return redirect(self.get_success_url())

        # Si el formset tiene errores
        return render(self.request, self.template_name, self.get_context_data(form=form))



# ----------------------------------------------------------
# ELIMINAR PROVEEDOR
# ----------------------------------------------------------
@method_decorator(permiso_requerido('proveedores.change_proveedor'), name='dispatch')
class ProveedorDeleteView(DeleteView):
    model = Proveedor
    success_url = reverse_lazy('proveedores:lista')

    def get(self, request, *args, **kwargs):
        proveedor = get_object_or_404(Proveedor, pk=kwargs['pk'])
        proveedor.delete()
        messages.success(request, f"Proveedor '{proveedor.razon_social}' eliminado correctamente.")
        return redirect(self.success_url)


# ----------------------------------------------------------
# DETALLE DEL PROVEEDOR
# ----------------------------------------------------------
class ProveedorDetailView(DetailView):
    model = Proveedor
    template_name = 'proveedores/detalle_proveedor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos_asociados'] = ProductoProveedor.objects.filter(proveedor=self.object)
        return context
