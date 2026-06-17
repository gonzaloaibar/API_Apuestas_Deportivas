import pytest
from apps.usuario.tests.fixture_usuario import *
from apps.servicio.ApiFootball import APIFootballService
from rest_framework import status

@pytest.mark.django_db
def test_error_fecha_importar_partidos(get_superuser_autenticado):
    try:
        resultado = APIFootballService.importar('2023-03-05','2023-03-01')
        assert False, "Deberia lanzar un ValueError"
    except ValueError as e:
        assert 'es posterior a la fecha' in str(e)

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



# @pytest.mark.django_db
# def test_no_existen_partidos_en_rango_de_fechas(moker):
#
#     sin_partidos_mock = {'results': 0, 'response': []}
#
#     moker.patch(
#         'apps.apuesta.api',
#         return_value = sin_partidos_mock
#     )
#
#     assert

