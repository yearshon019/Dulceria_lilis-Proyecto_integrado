from pyexpat.errors import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Producto
from .forms import ProductoForm
from django.shortcuts import get_object_or_404, redirect
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

def add_to_cart(request, pk):
    Producto =get_object_or_404(Producto, pk=pk)
    if Producto.stock_actual > 0:
        messages.success(request, f'El producto {Producto.nombre} ha sido agregado al carrito.')
    else:
        messages.error(request, f'El producto {Producto.nombre} no tiene stock disponible.')
    return redirect('productos:lista')

def mensajes(request):
    messages.add_message(request, messages.INFO, 'Esto es un mensaje de información.')
    messages.add_message(request, messages.SUCCESS, 'Esto es un mensaje de éxito.')
    messages.add_message(request, messages.WARNING, 'Esto es un mensaje de advertencia.')
    messages.add_message(request, messages.ERROR, 'Esto es un mensaje de error.')
    return redirect('productos:lista')
