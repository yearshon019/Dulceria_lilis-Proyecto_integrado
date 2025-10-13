from django.http import HttpResponse

def lista_proveedores(request):
    return HttpResponse("Lista de proveedores")

def crear_proveedor(request):
    return HttpResponse("Crear proveedor")

def editar_proveedor(request, pk):
    return HttpResponse(f"Editar proveedor {pk}")

def eliminar_proveedor(request, pk):
    return HttpResponse(f"Eliminar proveedor {pk}")

def detalle_proveedor(request, pk):
    return HttpResponse(f"Detalle del proveedor {pk}")