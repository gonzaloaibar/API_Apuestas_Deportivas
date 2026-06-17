import pytest
from rest_framework import status
from .fixtures_partido import *
from apps.usuario.tests.fixture_usuario import *

#------ ATENCION -------
#para trabajar con las fechas hay que tener el cuenta el formato que especificamos en el archivo .env-ejemplo
@pytest.mark.django_db
def test_terminar_partidos_exitoso(get_superuser_autenticado,crear_partidos,mocker):
    crear_partidos(
        api_football_id = '12345',
        equipo_local = 'Boca',
        equipo_visitante = 'River',
        estado = 'pendiente',
        fecha = '2023-05-01T20:00:00+00:00')
    crear_partidos(
        api_football_id='11',
        equipo_local='Racing',
        equipo_visitante='Independiente',
        estado='pendiente',
        fecha = '2023-05-01T22:30:00+00:00')

    mocker.patch('apps.apuesta.api.dotenv_values',return_value = {
            'FECHA_HORA_SIMULADA': '2023-05-01T22:10:00'  # fecha y hora despues del primer partido creado
        })

    respuesta = get_superuser_autenticado.patch('/api/partidos/terminar_partido/')

    assert respuesta.status_code == status.HTTP_200_OK
    assert Partido.objects.filter(estado='finalizado').count() == 1 #el partido de las 20hrs termino
    assert Partido.objects.filter(estado='pendiente').count() == 1 #el partido de las 22:30 aun no comeenzo segun nuestra hora simulada
    assert 'partidos terminados' in respuesta.data['resultado']
    assert 'Apuestas ejecutadas correctamente' in respuesta.data['mensaje']
    

@pytest.mark.django_db
def test_terminar_partido_fecha_anterior_al_partido(get_superuser_autenticado,crear_partidos,mocker):
    partido = crear_partidos(
        api_football_id = '12345',
        equipo_local = 'Boca',
        equipo_visitante = 'River',
        estado = 'pendiente',
        fecha = '2023-05-01T20:30:00+00:00')

    mocker.patch('apps.apuesta.api.dotenv_values',return_value = {
            'FECHA_HORA_SIMULADA': '2023-05-01T19:45:00+00:00'  # fecha y hora anterior all partido
        })

    respuesta = get_superuser_autenticado.patch('/api/partidos/terminar_partido/')


    assert respuesta.status_code == status.HTTP_200_OK

    #el partido debe quedar como pendiente todavia
    partido.refresh_from_db()
    assert partido.estado == 'pendiente'


@pytest.mark.django_db
def test_terminar_partido_error_en_fecha(get_superuser_autenticado,crear_partidos,mocker):
    crear_partidos(
        api_football_id = '10',
        equipo_local = 'Boca',
        equipo_visitante = 'River',
        estado = 'pendiente',
        fecha = '2023-05-01T20:30:00+00:00')

    mocker.patch('apps.apuesta.api.dotenv_values',return_value = {
            'FECHA_HORA_SIMULADA': 'fecha que no sigue el formato'
        })

    respuesta = get_superuser_autenticado.patch('/api/partidos/terminar_partido/')

    assert respuesta.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'Error en la fecha' in respuesta.data['error']


@pytest.mark.django_db
def test_filtrar_partidos_por_estado(get_usuario_autenticado, crear_partidos):
    crear_partidos(api_football_id='1',
                   equipo_local='Boca',
                   equipo_visitante='River',
                   estado='pendiente',
                   fecha='2023-05-01T20:30:00+00:00')
    crear_partidos(api_football_id='2',
                   equipo_local='Racing',
                   equipo_visitante='Independiente',
                   estado='finalizado',
                   fecha='2023-05-01T21:30:00+00:00')
    crear_partidos(api_football_id='3',
                   equipo_local='San Lorenzo',
                   equipo_visitante='Huracan',
                   estado='pendiente',
                   fecha='2023-05-02T18:00:00+00:00')

    respuesta = get_usuario_autenticado.get('/api/partidos/?estado=pendiente')

    assert respuesta.status_code == status.HTTP_200_OK
    assert len(respuesta.data['results']) == 2

@pytest.mark.django_db
def test_uuid_es_unico(crear_partidos):
    partido1 = crear_partidos(
        api_football_id=1,
        equipo_local='Boca',
        equipo_visitante='River',
        estado='pendiente',
        fecha='2023-05-01T20:00:00+00:00')
    partido2 = crear_partidos(
        api_football_id=2,
        equipo_local='Racing',
        equipo_visitante='Independiente',
        estado='pendiente',
        fecha='2023-05-02T20:00:00+00:00')

    assert partido1.uuid != partido2.uuid

@pytest.mark.django_db
def test_filtrar_partidos_por_equipo(crear_partidos,get_usuario_autenticado):
    crear_partidos(
        api_football_id=1,
        equipo_local='Boca',
        equipo_visitante='River',
        estado='pendiente',
        fecha='2023-05-01T20:00:00+00:00')
    crear_partidos(
        api_football_id=2,
        equipo_local='Racing',
        equipo_visitante='Independiente',
        estado='pendiente',
        fecha='2023-05-02T20:00:00+00:00')
    crear_partidos(
        api_football_id=3,
        equipo_local='Huracan',
        equipo_visitante='Boca',
        estado='pendiente',
        fecha='2023-05-05T20:00:00+00:00')

    respuesta = get_usuario_autenticado.get('/api/partidos/?equipo=BOc')

    assert len(respuesta.data['results']) == 2
    assert 'Boca' in respuesta.data['results'][0]['equipo_local']
    assert 'Boca' in respuesta.data['results'][1]['equipo_visitante']
    assert respuesta.status_code == status.HTTP_200_OK


