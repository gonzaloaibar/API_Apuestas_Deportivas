import pytest
from rest_framework import status

#from .fixtures_opcion_apuesta import get_opcion_apuesta
#from apps.usuario.tests.fixture_usuario import*
# from .fixtures_partido import*
# from .fixtures_apuesta import*

#TEST PARA CREAR UNA APUESTA CON UN CLIENTE AUNTENTICADO

@pytest.mark.django_db
def test_crear_apuesta(cliente_autenticado, get_opcion_goles):

    response = cliente_autenticado.post(
        "/api/apuestas/",
        {
            "opcion_apuesta": str(get_opcion_goles.uuid),
            "monto_apostado": "5000"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["estado"] == "pendiente"
    assert response.data["monto_apostado"] == "5000.00"

#TEST PARA CREAR UNA APUESTA CON UN USUARIO NO AUTENTICADO (NO SE DEBE PERMITIR)

@pytest.mark.django_db
def test_crear_apuesta_sin_autenticacion(api_client, opcion_resultado_local):
    #apiclient limpio sin credenciales
    response = api_client.post("/api/apuestas/", {
        "opcion_apuesta": str(opcion_resultado_local.uuid),
        "monto_apostado": "5000"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


#TEST PARA CREAR UNA APUESTA EN UN PARTIDO FINALIZADO (ACCION NO PERMITIDA)

@pytest.mark.django_db
def test_crear_apuesta_partido_finalizado(cliente_autenticado, opcion_apuesta_partido_finalizado):

    response = cliente_autenticado.post("/api/apuestas/", {
        "opcion_apuesta": str(opcion_apuesta_partido_finalizado.uuid),
        "monto_apostado": "5000"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    #Aqui pregunto si este mensaje esta en la data, ya que es el mensaje de la validacion en el serializador
    assert "No se puede apostar sobre un partido finalizado." in str(response.data)



@pytest.mark.django_db
def test_obtener_apuesta(get_usuario_autenticado, get_apuesta_pendiente):

    response = get_usuario_autenticado.get(
        f"/api/apuestas/{get_apuesta_pendiente.uuid}/"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["uuid"] == str(get_apuesta_pendiente.uuid)