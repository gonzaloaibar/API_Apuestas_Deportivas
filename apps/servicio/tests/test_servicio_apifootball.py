import pytest
import requests.exceptions

from apps.apuesta.excepciones import NoExistenPartidosError, FechasError
from apps.usuario.tests.fixture_usuario import *
from apps.servicio.ApiFootball import APIFootballService
from rest_framework import status

@pytest.mark.django_db
def test_error_fecha_importar_partidos(get_superuser_autenticado):
    try:
        resultado = APIFootballService.importar('2023-03-05','2023-03-01')
        assert False, "Deberia lanzar un ValueError"
    except FechasError as e:
        assert 'Error en las fechas ingresadas,por favor revisar' in str(e)


@pytest.mark.django_db
def test_importar_partidos_sin_fechas(get_superuser_autenticado):
    respuesta = get_superuser_autenticado.post('/api/partidos/importar_partidos/',{})
    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in respuesta.data

@pytest.mark.django_db
def test_importar_partidos_usuario_normal(get_usuario_autenticado):
    respuesta = get_usuario_autenticado.post('/api/partidos/importar_partidos/',{})
    assert respuesta.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_importar_partidos_existoso(get_superuser_autenticado,mocker):
    fechas = {
        'from': '2023-03-01',
        'to': '2023-03-02'
    }
    ##Se va asimular que se crean 4 partidos
    mocker.patch('apps.apuesta.api.APIFootballService.importar',return_value = 4)

    respuesta = get_superuser_autenticado.post('/api/partidos/importar_partidos/',fechas)

    assert respuesta.status_code == status.HTTP_201_CREATED
    assert 'se importaron correctamente 4 partidos' in respuesta.data['mensaje']


@pytest.mark.django_db
def test_importar_partidos_timeout(get_superuser_autenticado,mocker):
    fechas = {
        'from': '2023-03-01',
        'to': '2023-03-02'
    }

    mocker.patch('apps.apuesta.api.APIFootballService.importar',side_effect = requests.exceptions.Timeout()) #simula un Timeout

    respuesta = get_superuser_autenticado.post('/api/partidos/importar_partidos/',fechas)

    assert respuesta.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert 'El servicio externo tardó demasiado en responder.' in respuesta.data['error']

@pytest.mark.django_db
def test_importar_partidos_sin_conexion(get_superuser_autenticado,mocker):
    fechas = {
        'from': '2023-03-01',
        'to': '2023-03-02'
    }

    mocker.patch('apps.apuesta.api.APIFootballService.importar',side_effect = requests.exceptions.ConnectionError)

    respuesta = get_superuser_autenticado.post('/api/partidos/importar_partidos/',fechas)

    assert respuesta.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert 'No se pudo conectar al servicio externo. Inténtelo más tarde.' in respuesta.data['error']

@pytest.mark.django_db
def test_importar_partidos_no_encontrados_en_rango_fechas(get_superuser_autenticado,mocker):
    fechas = {
        'from': '2023-03-01',
        'to': '2023-03-02'
    }

    mocker.patch('apps.apuesta.api.APIFootballService.importar',side_effect = NoExistenPartidosError)

    respuesta = get_superuser_autenticado.post('/api/partidos/importar_partidos/',fechas)

    assert respuesta.status_code == status.HTTP_404_NOT_FOUND
    assert 'No existen partidos en el rango de fecha proporcionado' in respuesta.data['error']

@pytest.mark.django_db
def test_importar_partidos_ya_cargados_en_DB(get_superuser_autenticado,mocker):
    fechas = {
        'from': '2023-03-01',
        'to': '2023-03-02'
    }

    mocker.patch('apps.apuesta.api.APIFootballService.importar',return_value = 0)

    respuesta = get_superuser_autenticado.post('/api/partidos/importar_partidos/',fechas)

    assert respuesta.status_code == status.HTTP_200_OK
    assert 'El rango de fechas que ingreso corresponde a partidos que ya estan cargados' in respuesta.data['mensaje']



@pytest.mark.django_db
def test_importar_partidos_error_con_api_externa(get_superuser_autenticado,mocker):
    fechas = {
        'from': '2023-03-01',
        'to': '2023-03-02'
    }

    mocker.patch('apps.apuesta.api.APIFootballService.importar',side_effect = ValueError)

    respuesta = get_superuser_autenticado.post('/api/partidos/importar_partidos/',fechas)

    assert respuesta.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'error' in respuesta.data

