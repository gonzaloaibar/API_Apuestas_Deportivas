from django.urls import path
from apps.usuario.api import RegistroUsuarioAPIView, TraerUsuariosAPIView, ModificarSaldoAPIView

urlpatterns = [
    path('crear_usuario/', RegistroUsuarioAPIView.as_view()),
    path('ver_usuarios/',TraerUsuariosAPIView.as_view()),
    path('<int:pk>/modificar_saldo/', ModificarSaldoAPIView.as_view())
]