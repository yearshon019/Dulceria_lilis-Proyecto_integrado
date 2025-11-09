from django.db import models
from django.conf import settings


class SistemaPermisos(models.Model):
    class Meta:
        managed = False  # No crea tabla
        permissions = [
            ("ver_grafica", "Puede ver la gráfica"),
            ("ver_actividad", "Puede ver la actividad"),
        ]



class RegistroActividad(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Registro de actividad'
        verbose_name_plural = 'Registros de actividad'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} - {self.descripcion} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"
