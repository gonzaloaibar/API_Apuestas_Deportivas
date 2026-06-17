import pytest
from rest_framework import status

from .fixtures_opcion_apuesta import get_opcion_apuesta
from apps.usuario.tests.fixture_usuario import* #get_usuario_autenticado, api_client, token
from .fixtures_partido import*
from .fixtures_apuesta import*

@pytest.mark.django_db
def test_listar_apuesta(get_usuario_autenticado, get_apuesta):
    response = get_usuario_autenticado.get("/api/apuestas/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_crear_apuesta(
    get_usuario_autenticado,
    get_opcion_apuesta
):

    response = get_usuario_autenticado.post(
        "/api/apuestas/",
        {
            "opcion_apuesta": str(get_opcion_apuesta.uuid),
            "monto_apostado": "5000"
        },
        format="json"
    )

    assert response.status_code == 201
