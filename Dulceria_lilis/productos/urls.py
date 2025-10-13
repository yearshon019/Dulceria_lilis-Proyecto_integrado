# productos/urls.py
from django.urls import path
from django.http import HttpResponse

app_name = 'productos'

def temporal(request):
    return HttpResponse("Ruta temporal de productos funcionando")

urlpatterns = [
    path('', temporal, name='lista'),
]
