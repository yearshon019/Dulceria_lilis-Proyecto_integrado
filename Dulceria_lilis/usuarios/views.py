from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    # Página mínima de perfil para usuarios autenticados
    return render(request, 'usuarios/perfil.html', {'user': request.user})
