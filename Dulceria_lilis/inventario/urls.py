from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.MovimientoInventarioListView.as_view(), name='inicio'),
    path('movimiento/nuevo/', views.MovimientoInventarioCreateView.as_view(), name='crear_movimiento'),
    path('movimiento/<int:pk>/', views.MovimientoInventarioDetailView.as_view(), name='detalle_movimiento'),
<<<<<<< HEAD
    path('bodegas/', views.BodegaListView.as_view(), name='lista_bodegas'),
=======
    path('bodegas/', views.BodegaListView.as_view(), name='bodegas'),
>>>>>>> 35238ce3c7b5ffbc00cce3e386f10ecdd91faba0
]
