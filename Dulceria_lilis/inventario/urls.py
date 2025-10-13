# inventario/urls.py
from django.urls import path
from django.http import HttpResponse

app_name = 'inventario'

def temporal(request):
    return HttpResponse("Ruta temporal de inventario funcionando")

urlpatterns = [
    path('', temporal, name='inicio'),
]
