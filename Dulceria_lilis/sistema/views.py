from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def dashboard(request):
    # Recuperar el contador de visitas de la sesión
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1

    # Ejemplos de mensajes (estos se mostrarán en tu plantilla)
   # messages.success(request, 'Producto agregado al carrito correctamente.')
    #messages.error(request, 'Stock insuficiente para completar la operación.')

    # Renderizar el panel principal
    return render(request, 'dashboard.html', {'visitas': visitas})

@login_required
def cambiar_clave(request):
    # ✅ Crear una clave de sesión
    request.session['productos'] = {'sku': 1}
    messages.success(request, 'Clave "productos" creada en la sesión.')

    # ✅ Si quisieras eliminarla (hazlo en otra vista)
    # if 'productos' in request.session:
    #     del request.session['productos']
    #     messages.error(request, 'Clave "productos" eliminada de la sesión.')

    return redirect('dashboard.html')

