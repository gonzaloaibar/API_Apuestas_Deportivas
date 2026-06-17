import pytest
from rest_framework.test import APIClient
from apps.usuario.models import Usuario

from .fixtures_opcion_apuesta import get_opcion_apuesta
from .fixtures_partido import *

@pytest.fixture
def usuario():
    return Usuario.objects.create_user(
        username="test",
        password="1234",
        nombre="Test",
        apellido="Usuario",
        cuil="20123456789",
        saldo=50000
    )

@pytest.fixture
def api_client_autenticado(usuario):

    client = APIClient()

    client.force_authenticate(
        user=usuario
    )

    return client

@pytest.mark.django_db
def test_crear_apuesta(
    api_client_autenticado,
    get_opcion_apuesta
):

    response = api_client_autenticado.post(
        "/api/apuestas/",
        {
            "opcion_apuesta": str(get_opcion_apuesta.uuid),
            "monto_apostado": "5000"
        },
        format="json"
    )

    assert response.status_code == 201
