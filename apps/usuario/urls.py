from django.urls import path
from apps.usuario.api import RegistroUsuarioAPIView

urlpatterns = [
    path('crear_usuario/', RegistroUsuarioAPIView.as_view())
]