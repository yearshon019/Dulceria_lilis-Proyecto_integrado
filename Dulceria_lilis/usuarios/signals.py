from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

@receiver(user_logged_in)
def actualizar_ultimo_acceso(sender, request, user, **kwargs):
    user.ultimo_acceso = timezone.now()
    user.save(update_fields=['ultimo_acceso'])
