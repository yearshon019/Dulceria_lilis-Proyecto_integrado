from django.contrib import admin
from django.urls import path, include
from .views import dashboard
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),  # home
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    # otras includes:
    path('productos/', include('productos.urls', namespace='productos')),
    path('inventario/', include('inventario.urls', namespace='inventario')),
    path('proveedores/', include('proveedores.urls', namespace='proveedores')),
    path('cambiar_clave/', views.cambiar_clave, name='cambiar_clave'),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)