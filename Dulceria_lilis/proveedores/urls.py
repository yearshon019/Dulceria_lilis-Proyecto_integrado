# proveedores/urls.py
from django.urls import path
from django.http import HttpResponse

app_name = 'proveedores'

def temporal(request):
    return HttpResponse("Ruta temporal de proveedores funcionando")

urlpatterns = [
    path('', temporal, name='inicio'),
]
