# proveedores/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from .models import Proveedor, ProductoProveedor
from .forms import ProveedorForm, ProductoProveedorFormSet
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
        qs = super().get_queryset().order_by('razon_social')
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
        if 'form' not in ctx:
            ctx['form'] = ProveedorForm()
        ctx['titulo'] = 'Registrar proveedor'
        return ctx

    def post(self, request, *args, **kwargs):
        form = ProveedorForm(request.POST)

        if form.is_valid():
            rut = form.cleaned_data.get('rut_nif')
            email = form.cleaned_data.get('email')
            if Proveedor.objects.filter(rut_nif=rut).exists():
                form.add_error('rut_nif', 'Ya existe un proveedor con este RUT/NIF.')
            if Proveedor.objects.filter(email=email).exists():
                form.add_error('email', 'Ya existe un proveedor con este correo electrónico.')

        if form.errors:
            messages.error(request, 'Por favor complete todos los campos obligatorios correctamente.')
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

        form.save()
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
        if self.request.POST:
            context["pp_formset"] = ProductoProveedorFormSet(self.request.POST, instance=self.object)
        else:
            context["pp_formset"] = ProductoProveedorFormSet(instance=self.object)
        context['titulo'] = 'Editar'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pp_formset = context["pp_formset"]

        if pp_formset.is_valid():
            self.object = form.save()
            pp_formset.instance = self.object
            pp_formset.save()
            messages.success(self.request, "Proveedor y productos asociados guardados correctamente.")
            return redirect(self.get_success_url())
        else:
            return render(self.request, self.template_name, self.get_context_data(form=form))

    def form_invalid(self, form):
        if form.errors:
            messages.error(self.request, 'Por favor, corrija los errores.')
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
