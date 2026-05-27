from django.urls import path
from apps.usuario.api import APIViewUsuario

urlpatterns = [
    path('crear_usuario/',APIViewUsuario.as_view())
]