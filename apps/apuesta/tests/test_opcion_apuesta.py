import pytest
from rest_framework import status
from apps.apuesta.models import OpcionApuesta
from apps.apuesta.tests.fixtures_opcion_apuesta import *
from apps.apuesta.tests.fixtures_partido import crear_partidos, get_partido,get_partido_finalizado
from apps.usuario.tests.fixture_usuario import * #api_client, get_superuser,crear_superuser


@pytest.mark.django_db
def test_opcion_apuesta_partido_finalizado(get_partido_finalizado,get_superuser_autenticado):

    usuario = get_superuser_autenticado

    respuesta = usuario.post('/api/opcion_de_apuestas/', {
        'partido' : get_partido_finalizado.uuid,
        'tipo_apuesta' : 'resultado',
        'prediccion' : 'E',
        'multiplicador': '2.5',
        'monto_minimo' : '5000'
    })

    assert 'non_field_errors' in respuesta.json()
    assert "No puede crear una opción de apuesta en un partido finalizado." == respuesta.json()['non_field_errors'][0]
    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_opcion_apuesta_prediccion_resultado_no_valida(get_partido,get_superuser_autenticado):

    usuario = get_superuser_autenticado

    respuesta = usuario.post('/api/opcion_de_apuestas/', {
        'partido' : get_partido.uuid,
        'tipo_apuesta' : 'resultado',
        "prediccion": "mas_1_gol",
        'multiplicador': '2.5',
        'monto_minimo' : '5000'
    })

    assert 'prediccion' in respuesta.json()
    assert "La predicción no corresponde a una apuesta de resultado." == respuesta.json()['prediccion'][0]
    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_opcion_apuesta_usuario_normal(get_partido,get_usuario_autenticado):

    usuario = get_usuario_autenticado

    respuesta = usuario.post('/api/opcion_de_apuestas/', {
        'partido' : get_partido.uuid,
        'tipo_apuesta' : 'resultado',
        "prediccion": "E",
        'multiplicador': '2.5',
        'monto_minimo' : '5000'
    })

    assert respuesta.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_opcion_apuesta_usuario_no_autenticado(get_partido,api_client):

    usuario = api_client


    respuesta = usuario.post('/api/opcion_de_apuestas/', {
        'partido' : get_partido.uuid,
        'tipo_apuesta' : 'resultado',
        "prediccion": "E",
        'multiplicador': '2.5',
        'monto_minimo' : '5000'
    })

    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_eliminar_opcion_apuesta(get_opcion_apuesta,get_superuser_autenticado):

    opcion_apuesta_uuid = get_opcion_apuesta.uuid
    #print(f'uuid = {opcion_apuesta_uuid}')

    respuesta = get_superuser_autenticado.delete(f'/api/opcion_de_apuestas/{opcion_apuesta_uuid}/')

    assert respuesta.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_modificar_opcion_apuesta(get_opcion_apuesta, get_superuser_autenticado):

    datos = {
    "prediccion": "L",
    "monto_minimo": "60000"
    }
    opcion_apuesta_uuid = get_opcion_apuesta.uuid

    respuesta = get_superuser_autenticado.patch(f'/api/opcion_de_apuestas/{opcion_apuesta_uuid}/',datos)

    assert respuesta.status_code == status.HTTP_200_OK
    assert 'L' in respuesta.data['prediccion']
    assert '60000' in respuesta.data['monto_minimo']


