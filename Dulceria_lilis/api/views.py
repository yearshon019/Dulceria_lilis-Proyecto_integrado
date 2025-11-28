<<<<<<< HEAD
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from productos.models import Producto
from .serializers import ProductoSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import Http404, JsonResponse
=======
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from productos.models import Producto
from .serializers import ProductoSerializer
>>>>>>> c9bd708 (cloude)
def info(request):
    return JsonResponse({

  "proyecto": "vamos a la luna",

  "version": "1.0",

  "autor": "kevin ayala supremo"

})

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
<<<<<<< HEAD
    permission_classes = [IsAuthenticated, permissions.DjangoModelPermissions]

# -----------------------------
    # 1) Controlar 404 (Not Found)
    # -----------------------------
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Producto no encontrado master")

    # -----------------------------
    # 2) Respuesta 200 OK
    # -----------------------------
    def list(self, request, *args, **kwargs):
        productos = self.get_queryset()
        serializer = self.get_serializer(productos, many=True)
        return Response(
            {"status": 200, "mensaje": "Todo bien master", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    # -----------------------------
    # 3) Respuesta 201 CREATED
    # -----------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": 400, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(
            {"status": 201, "mensaje": "Producto creado con éxito", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    # -----------------------------
    # 4) Respuestas 400 / 401 / 403
    # -----------------------------
    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"status": 401, "error": "No autorizado"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.has_perm('productos.change_producto'):
            return Response(
                {"status": 403, "error": "No tienes permisos para modificar"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(self.get_object(), data=request.data)

        if not serializer.is_valid():
            return Response(
                {"status": 400, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_update(serializer)
        return Response(
            {"status": 200, "mensaje": "Producto actualizado", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    # -----------------------------
    # 5) Respuesta 500 (Server Error)
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        try:
            producto = self.get_object()
            producto.delete()
            return Response(
                {"status": 200, "mensaje": "Producto eliminado master"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"status": 500, "error": f"Error interno: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        
=======
    permission_classes = [IsAuthenticated]
>>>>>>> c9bd708 (cloude)
