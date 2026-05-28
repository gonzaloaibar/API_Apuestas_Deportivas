from django.urls import path
from apps.usuario.api import RegistroUsuarioAPIView, TraerUsuariosAPIView, CargarSaldoAPIView

urlpatterns = [
    path('crear_usuario/', RegistroUsuarioAPIView.as_view()),
    path('ver_usuarios/',TraerUsuariosAPIView.as_view()),
    path('<int:pk>/cargar_saldo/', CargarSaldoAPIView.as_view())
]