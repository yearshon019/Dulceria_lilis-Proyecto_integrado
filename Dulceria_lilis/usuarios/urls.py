from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from . import views

app_name = 'usuarios'

urlpatterns = [
    # 🔐 Login y Logout
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 👤 Perfil
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.perfil_editar, name='perfil_editar'),

    # 👥 CRUD de usuarios
    path('', views.usuario_list, name='lista_usuarios'),
    path('', views.usuario_list, name='lista'),  # Alias
    path('crear/', views.usuario_create, name='crear'),
    path('<int:pk>/editar/', views.usuario_update, name='editar'),
    path('<int:pk>/eliminar/', views.usuario_delete, name='eliminar'),

    # 💌 Recuperación de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset.html'
    ), name='password_reset'),

    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'
    ), name='password_reset_complete'),
]
