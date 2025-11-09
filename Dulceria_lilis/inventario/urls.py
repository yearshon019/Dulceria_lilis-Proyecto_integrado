from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.MovimientoInventarioListCreateView.as_view(), name='inicio'),
    path('movimiento/<int:pk>/editar/', views.MovimientoInventarioUpdateView.as_view(), name='editar_movimiento'),
    path('movimiento/<int:pk>/', views.MovimientoInventarioDetailView.as_view(), name='detalle_movimiento'),
    path('bodegas/', views.BodegaListView.as_view(), name='lista_bodegas'),
]
