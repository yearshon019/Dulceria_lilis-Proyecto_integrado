from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Producto
from .forms import ProductoForm

class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'object_list'
    paginate_by = 25

class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/form.html'
    success_url = reverse_lazy('productos:lista')

class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/form.html'
    success_url = reverse_lazy('productos:lista')

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'productos/confirm_delete.html'
    success_url = reverse_lazy('productos:lista')

class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/detail.html'
