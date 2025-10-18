from django.urls import path
from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    ProductoDetailView
)

app_name = 'productos'

urlpatterns = [
    path('', ProductoListView.as_view(), name='lista'),
    path('nuevo/', ProductoCreateView.as_view(), name='crear'),
    path('editar/<int:pk>/', ProductoUpdateView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='eliminar'),
    path('detalle/<int:pk>/', ProductoDetailView.as_view(), name='detalle'),
]