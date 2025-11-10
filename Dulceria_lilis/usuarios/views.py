from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .forms import UsuarioForm, PerfilForm
from .models import Usuario
from utils.export_excel import queryset_to_excel

# --- 💌 Recuperación de contraseña simplificada con SweetAlert ---
from .models import Usuario
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

# 🧑‍💻 PERFIL DEL USUARIO
@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html', {'user': request.user})


@login_required
def perfil_editar(request):
    """Permite al usuario editar su propio perfil."""
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("usuarios:perfil")
        messages.error(request, "Hay errores en el formulario. Revisa los campos.")
    else:
        form = PerfilForm(instance=request.user, user=request.user)

    return render(request, "usuarios/perfil_editar.html", {"form": form})


# 👥 LISTADO Y EXPORTACIÓN DE USUARIOS
@login_required
def usuario_list(request):
    """
    Lista con filtros (q, rol, estado) y formulario embebido para crear.
    Además permite exportar los resultados a Excel.
    """
    qs = Usuario.objects.all().order_by('username')

    q = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '').strip()
    estado = request.GET.get('estado', '').strip()

    if q:
        qs = qs.filter(username__icontains=q)
    if rol:
        qs = qs.filter(rol=rol)
    if estado:
        qs = qs.filter(estado=estado)

    # 📤 Exportar a Excel
    if request.GET.get("export") == "xlsx":
        columns = [
            ("Username", lambda u: u.username),
            ("Email", lambda u: u.email),
            ("Nombre", lambda u: f"{u.nombres or ''} {u.apellidos or ''}".strip()),
            ("Teléfono", lambda u: u.telefono or ""),
            ("Rol", lambda u: u.rol),
            ("Estado", lambda u: u.estado),
            ("Área", lambda u: u.area or ""),
            ("MFA habilitado", lambda u: "Sí" if u.mfa_habilitado else "No"),
            ("Último acceso", lambda u: u.last_login.replace(tzinfo=None) if u.last_login else ""),
        ]
        raw, fname = queryset_to_excel("usuarios", columns, qs)
        resp = HttpResponse(
            raw,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{fname}"'
        return resp

    form = UsuarioForm()  # Form vacío para crear usuario
    ctx = {
        'usuarios': qs,
        'form': form,
        'f_q': q,
        'f_rol': rol,
        'f_estado': estado,
    }
    return render(request, 'usuarios/Lista_usuario.html', ctx)


# ➕ CREAR USUARIO
@login_required
@permission_required('usuarios.add_usuario', raise_exception=False)
@require_POST
def usuario_create(request):
    form = UsuarioForm(request.POST)
    if form.is_valid():
        usuario = form.save(commit=False)

        # 🔐 Manejo de contraseña
        password = form.cleaned_data.get('password')
        if password:
            usuario.set_password(password)
        else:
            usuario.set_password('123456')  # Contraseña por defecto opcional

        usuario.save()
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('usuarios:lista')

    # ❌ Si hay errores, volver a mostrar lista con formulario
    qs = Usuario.objects.all().order_by('username')
    ctx = {
        'usuarios': qs,
        'form': form,
        'f_q': request.GET.get('q', ''),
        'f_rol': request.GET.get('rol', ''),
        'f_estado': request.GET.get('estado', ''),
    }
    messages.error(request, 'Revisa los errores del formulario.')
    return render(request, 'usuarios/Lista_usuario.html', ctx)


# ✏️ EDITAR USUARIO
@login_required
@permission_required('usuarios.change_usuario', raise_exception=False)
def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            usuario.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuarios:lista')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/form_usuario.html', {
        'form': form,
        'obj': usuario,
        'modo': 'Editar'
    })


# 🗑️ ELIMINAR USUARIO
@login_required
@permission_required('usuarios.delete_usuario', raise_exception=False)
@require_POST
def usuario_delete(request, pk):
    u = get_object_or_404(Usuario, pk=pk)
    u.delete()
    messages.success(request, 'Usuario eliminado.')
    return redirect('usuarios:lista')


# 🔑 Recuperación de contraseña personalizada

# 💌 Paso 1: Solicitar correo
def password_reset_custom(request):
    """
    Muestra el formulario para ingresar el correo o usuario y envía el enlace.
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = Usuario.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = f"{'https' if request.is_secure() else 'http'}://{request.get_host()}/usuarios/reset/{uid}/{token}/"

                subject = "Restablecer contraseña - Dulcería Lili"
                message = f"Hola {user.username},\n\nHaz clic en el siguiente enlace para crear una nueva contraseña:\n\n{reset_link}\n\nSi no solicitaste esto, puedes ignorar este mensaje."
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            # ⚡️ Redirige con parámetro de éxito (aunque el correo no exista)
            return redirect('/usuarios/password_reset/?sent=true')
    else:
        form = PasswordResetForm()

    return render(request, 'usuarios/password_reset.html', {'form': form})


# 🔐 Paso 2: Cambiar contraseña
def password_reset_confirm_custom(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                # ✅ redirigir a una página nueva, no volver al token
                return redirect("/usuarios/password_reset_done/?success=true")
            else:
                return render(request, 'usuarios/password_reset_confirm.html', {
                    'form': form,
                    'error': form.errors
                })
        else:
            form = SetPasswordForm(user)
        return render(request, 'usuarios/password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'usuarios/password_reset_confirm.html', {
            'error': 'El enlace no es válido o ha expirado.'
        })


def password_reset_done_custom(request):
    return render(request, 'usuarios/password_reset_done.html')
