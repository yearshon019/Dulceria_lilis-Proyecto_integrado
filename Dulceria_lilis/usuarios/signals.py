# usuarios/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    """
    Se ejecuta cada vez que un usuario inicia sesión correctamente.
    Actualiza la fecha de último acceso y cuenta las veces que ha iniciado sesión.
    """
    # Actualiza el último acceso
    user.ultimo_acceso = timezone.now()

    # Incrementa el contador de sesiones iniciadas
    if user.sesiones is None:
        user.sesiones = 1
    else:
        user.sesiones += 1

    user.save(update_fields=['ultimo_acceso', 'sesiones'])
