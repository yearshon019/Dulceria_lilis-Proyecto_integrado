from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Login usando la vista genérica de Django con nuestro LoginForm
    path('login/', auth_views.LoginView.as_view(
            template_name='usuarios/login.html',
            authentication_form=LoginForm,
            redirect_authenticated_user=True
        ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Perfil simple
    path('perfil/', views.perfil, name='perfil'),
]
