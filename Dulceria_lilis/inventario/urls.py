from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.MovimientoInventarioListView.as_view(), name='inicio'),
    path('movimiento/nuevo/', views.MovimientoInventarioCreateView.as_view(), name='crear_movimiento'),
    path('movimiento/<int:pk>/', views.MovimientoInventarioDetailView.as_view(), name='detalle_movimiento'),
    path('bodegas/', views.BodegaListView.as_view(), name='bodegas'),
]
