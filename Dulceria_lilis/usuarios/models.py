from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # Campos extra opcionales solicitados en el requerimiento
    nombres = models.CharField("Nombres", max_length=150, blank=True, null=True)
    apellidos = models.CharField("Apellidos", max_length=150, blank=True, null=True)
    telefono = models.CharField("Teléfono", max_length=30, blank=True, null=True)
    rol = models.CharField("Rol", max_length=50, default='Usuario')  # ej. Admin, Bodega, Vendedor
    estado = models.CharField("Estado", max_length=20, default='ACTIVO')  # ACTIVO, BLOQUEADO
    mfa_habilitado = models.BooleanField("MFA habilitado", default=False)
    ultimo_acceso = models.DateTimeField("Último acceso", blank=True, null=True)
    area = models.CharField("Área/Unidad", max_length=100, blank=True, null=True)
    observaciones = models.TextField("Observaciones", blank=True, null=True)

    def __str__(self):
        # Si hay nombres y apellidos, mostrar nombre completo; si no, username
        nombre_completo = ' '.join(filter(None, [self.nombres, self.apellidos])).strip()
        return nombre_completo or self.get_full_name() or self.username
