import pytest
from django.contrib.auth.models import Group, Permission
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.usuario.tests.fixture_usuario import crear_usuario

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def grupo_cliente(db):
    grupo, _ = Group.objects.get_or_create(name="Cliente")
    # asignás solo los permisos definidos en el admin
    permisos = Permission.objects.filter(codename__in=[
        "add_apuesta",
        "view_apuesta",
        "change_apuesta",
        "delete_apuesta",
        "view_opcion_apuesta",
        "view_partido"
    ])
    grupo.permissions.set(permisos)
    return grupo

@pytest.fixture
def grupo_administrador(db):
    grupo, _ = Group.objects.get_or_create(name="Administrador")
    # todos los permisos
    grupo.permissions.set(Permission.objects.all())
    return grupo

@pytest.fixture
def get_usuario_cliente(db, grupo_cliente):
    usuario = crear_usuario(username='cliente_test', cuil='11111111111')
    usuario.groups.add(grupo_cliente)
    return usuario

@pytest.fixture
def get_usuario_administrador(db, grupo_administrador):
    usuario = crear_usuario(username='admin_test', cuil='22222222222')
    usuario.groups.add(grupo_administrador)
    return usuario

@pytest.fixture
def cliente_autenticado(get_usuario_cliente):
    refresh = RefreshToken.for_user(get_usuario_cliente)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client

@pytest.fixture
def administrador_autenticado(get_usuario_administrador):
    refresh = RefreshToken.for_user(get_usuario_administrador)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client

@pytest.fixture
def get_usuario(db):
    return crear_usuario(username='probando', cuil='123456789')

@pytest.fixture
def get_usuario_autenticado(get_usuario):     # get_usuario ya tiene db
    refresh = RefreshToken.for_user(get_usuario)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client