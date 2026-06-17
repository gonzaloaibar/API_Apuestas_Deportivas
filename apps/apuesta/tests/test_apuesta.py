import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from apps.usuario.tests.fixture_usuario import crear_usuario
from .conftest import crear_apuesta
from ..api import resolver_apuesta_ganada
from ..models import OpcionApuesta, TipoApuesta, Prediccion
from decimal import Decimal


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


#TEST PARA OBTENER UNA APUESTA CON UN CLIENTE AUTENTICADO

@pytest.mark.django_db
def test_obtener_apuesta(cliente_autenticado, get_apuesta_pendiente):

    response = cliente_autenticado.get(
        f"/api/apuestas/{get_apuesta_pendiente.uuid}/"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["uuid"] == str(get_apuesta_pendiente.uuid)

#TEST PARA OBTENER UNA APUESTA AJENA A UN CLIENTE

@pytest.mark.django_db
def test_obtener_apuesta_de_otro_usuario(cliente_autenticado, crear_apuesta):

    #creo otro usuario
    Usuario = get_user_model()

    usuario_dueño = Usuario.objects.create_user(
        username="user_dueño",
        cuil="66666677777",
        password="password123",
        nombre="Testing",
        apellido="Testing",
    )

    apuesta_usuario_dueño = crear_apuesta(apostado_por=usuario_dueño)

    response = cliente_autenticado.get(
        f"/api/apuestas/{apuesta_usuario_dueño.uuid}/"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    #assert "propias apuestas" in str(response.data).lower()


#TEST PARA LA VALIDACION DEL MONTO MINIMO

@pytest.mark.django_db
def test_crear_apuesta_monto_menor_al_minimo(cliente_autenticado, opcion_apuesta):
    # get_opcion_apuesta tiene monto_minimo=100.00
    response = cliente_autenticado.post("/api/apuestas/", {
        "opcion_apuesta": str(opcion_apuesta.uuid),
        "monto_apostado": "10"        # menor al mínimo
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "monto" in str(response.data).lower()


#TEST PARA LA VALIDACION DE LA PREDICCION DUPLICADA

@pytest.mark.django_db
def test_crear_apuesta_prediccion_duplicada(cliente_autenticado, opcion_resultado_local, get_apuesta_pendiente):
    # get_apuesta_pendiente ya existe con la misma opcion y mismo usuario
    response = cliente_autenticado.post("/api/apuestas/", {
        "opcion_apuesta": str(opcion_resultado_local.uuid),
        "monto_apostado": "5000"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "predicción" in str(response.data).lower()


#TEST PARA MODIFICAR EL MONTO Y OPCIO DE UNA APUESTA

@pytest.mark.django_db
def test_modificar_monto_y_opcion_exitoso(cliente_autenticado, get_apuesta_pendiente, get_partido):
    nueva_opcion = OpcionApuesta.objects.create(
        partido=get_partido,
        tipo_apuesta=TipoApuesta.GOLES,
        prediccion=Prediccion.MAS_3_GOLES,
        multiplicador="2.50",
        monto_minimo="100.00",
    )
    response = cliente_autenticado.patch(
        f"/api/apuestas/{get_apuesta_pendiente.uuid}/modificar_apuesta/",
        {
            "opcion_apuesta": str(nueva_opcion.uuid),
            "monto_apostado": Decimal("300.00")
        }
    )
    assert response.status_code == status.HTTP_200_OK

    get_apuesta_pendiente.refresh_from_db()
    assert get_apuesta_pendiente.monto_apostado == Decimal("300.00")
    assert get_apuesta_pendiente.opcion_apuesta == nueva_opcion


#TEST RESOLVER APUESTA GANADA
@pytest.mark.django_db
def test_resolver_apuesta_ganada(get_apuesta_pendiente, mocker):
    mocker.patch(
        "apps.apuesta.api.dotenv_values",
        return_value={"PORCENTAJE_DE_COMISION": "0.10"}
    )
    opcion = get_apuesta_pendiente.opcion_apuesta  # multiplicador 1.80
    usuario = get_apuesta_pendiente.apostado_por
    saldo_inicial = usuario.saldo                  # 10000.00

    resolver_apuesta_ganada(get_apuesta_pendiente, opcion)

    # verificamos la apuesta
    get_apuesta_pendiente.refresh_from_db()
    assert get_apuesta_pendiente.estado == "ganada"

    # verificamos los calculos
    # monto: 500, multiplicador: 1.80
    # premio_parcial = 500 * 1.80 = 900
    # ganancia = 900 - 500 = 400
    # comision = 400 * 0.10 = 40
    # premio_final = 900 - 40 = 860
    assert get_apuesta_pendiente.ganancia_cliente == Decimal("860.00")
    assert get_apuesta_pendiente.ganancia_casa == Decimal("40.00")

    # verificamos el saldo del usuario
    usuario.refresh_from_db()
    assert usuario.saldo == saldo_inicial + Decimal("860.00")


#TEST PARA CONSULTAR GANANCIAS DE LA CASA CON UN CLIENTE NORMAL

@pytest.mark.django_db
def test_ganancias_casa_cliente_no_autorizado(cliente_autenticado):
    response = cliente_autenticado.get("/api/apuestas/ganancias_casa/")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "administradores" in str(response.data).lower()


#TEST PARA CONSULTAR GANANCIAS DE LA CASA CON UN USUARIO SIN AUTENTICAR

@pytest.mark.django_db
def test_ganancias_casa_sin_autenticacion(api_client):
    response = api_client.get("/api/apuestas/ganancias_casa/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED