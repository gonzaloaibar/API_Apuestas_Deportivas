import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

Usuario = get_user_model()

def crear_usuario(username,cuil,saldo = 10000,password='password123',nombre='Testing',apellido='Testing'):

    usuario, creado = Usuario.objects.get_or_create(username=username)

    if creado:
        usuario.cuil = cuil
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.saldo = saldo
        usuario.set_password(password)
        usuario.save()

    return usuario

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def get_usuario():
    usuario_de_test = crear_usuario(username='probando',cuil='123456789')
    return usuario_de_test

@pytest.fixture
def token(get_usuario):
    refresh = RefreshToken.for_user(get_usuario)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }

@pytest.fixture
def get_usuario_autenticado(token,api_client):
    #token = Token.objects.get_or_create(user = get_usuario)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
    return api_client

@pytest.fixture
def crear_superuser():
    User = get_user_model()
    user = User.objects.create_superuser(
        username="admin",
        nombre="nombretest",
        apellido="apellidotest",
        password='admin',
        is_superuser = True
    )
    return user

@pytest.fixture
def get_superuser(crear_superuser):
    usuario = crear_superuser
    return usuario

@pytest.fixture
def get_superuser_autenticado(api_client,crear_superuser):
    refresh = RefreshToken.for_user(crear_superuser)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client
