from django.urls import path
from apps.usuario.api import RegistroUsuarioAPIView, TraerUsuariosAPIView

urlpatterns = [
    path('crear_usuario/', RegistroUsuarioAPIView.as_view()),
    path('ver_usuarios/',TraerUsuariosAPIView.as_view()),

]