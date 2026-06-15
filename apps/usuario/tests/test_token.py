import pytest
from rest_framework import status

from .fixture_usuario import crear_usuario, api_client, get_usuario,token,get_usuario_autenticado

@pytest.mark.django_db
def test_obtener_token(api_client):
    #preparar las entradas
    usuario = crear_usuario(username='usuario_token',password='usuario_token',cuil='1234567810')

    #acturar
    respuesta = api_client.post('/api/token/',data={
        'username' : usuario.username,
        'password' : 'usuario_token'
    })

    # afirmar
    assert respuesta.status_code == 200
    assert 'access' in respuesta.data
    assert 'refresh' in respuesta.data

@pytest.mark.django_db
def test_usuario_sin_token(api_client):
    usuario = crear_usuario(username='usuario_token',password='usuario_token',cuil='1234567810')

    #acturar
    respuesta = api_client.get('/api/apuestas/')

    assert respuesta.status_code == status.HTTP_401_UNAUTHORIZED

