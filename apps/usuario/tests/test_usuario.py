from decimal import Decimal

import pytest
from rest_framework import status
from .fixture_usuario import *
from ..excepciones import SaldoInsuficienteException
from ...apuesta.api import resolver_apuesta_perdida, comprobar_saldo


@pytest.mark.django_db
def test_superuser(crear_superuser):
    super_usuario = crear_superuser

    assert super_usuario.is_staff == True
    assert super_usuario.is_active == True
    assert super_usuario.username == 'admin'


@pytest.mark.django_db
def test_cargar_saldo_usuario(get_usuario_autenticado,get_usuario,mocker):
    mocker.patch('apps.usuario.api.dotenv_values', return_value={
        'CODIGO_DE_RECARGA': 'RECARGA_SALDO12456'
    })

    respuesta = get_usuario_autenticado.post(f'/usuario/{get_usuario.id}/modificar_saldo/',{
        'codigo':'RECARGA_SALDO12456',
        'monto': 2500
    })

    assert respuesta.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_cargar_saldo_monto_error(get_usuario_autenticado,get_usuario,mocker):
    mocker.patch('apps.usuario.api.dotenv_values', return_value={
        'CODIGO_DE_RECARGA': 'RECARGA_SALDO12456'
    })

    respuesta = get_usuario_autenticado.post(f'/usuario/{get_usuario.id}/modificar_saldo/',{
        'codigo':'RECARGA_SALDO12456',
        'monto': -2500
    })

    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST
    assert 'El monto ingresado no es valido' in respuesta.data['error']


@pytest.mark.django_db
def test_retirar_saldo_usuario(get_usuario_autenticado, get_usuario, mocker):
    mocker.patch('apps.usuario.api.dotenv_values', return_value={
        'CODIGO_DE_RETIRO': 'RETIRO_SALDO12456'
    })

    respuesta = get_usuario_autenticado.post(f'/usuario/{get_usuario.id}/modificar_saldo/', {
        'codigo': 'RETIRO_SALDO12456',
        'monto': 2500
    })

    assert respuesta.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retirar_saldo_insuficiente(get_usuario_autenticado, get_usuario, mocker):
    mocker.patch('apps.usuario.api.dotenv_values', return_value={
        'CODIGO_DE_RETIRO': 'RETIRO_SALDO12456'
    })

    respuesta = get_usuario_autenticado.post(f'/usuario/{get_usuario.id}/modificar_saldo/', {
        'codigo': 'RETIRO_SALDO12456',
        'monto': 25000000
    })

    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Saldo insuficinte para realizar esta accción' in respuesta.data['error']


@pytest.mark.django_db
def test_retirar_error_codigo(get_usuario_autenticado, get_usuario, mocker):
    mocker.patch('apps.usuario.api.dotenv_values', return_value={
        'CODIGO_DE_RETIRO': 'RETIRO_SALDO12456'
    })

    respuesta = get_usuario_autenticado.post(f'/usuario/{get_usuario.id}/modificar_saldo/', {
        'codigo': 'lkasmdfad',
        'monto': 1500
    })

    assert respuesta.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Código de solicitud inválido' in respuesta.data['error']

@pytest.mark.django_db
def test_usuario_no_encontrado(get_usuario_autenticado, mocker):
    mocker.patch(
        'apps.usuario.api.dotenv_values',
        return_value={'CODIGO_DE_RECARGA': 'RECARGA_SALDO12456'}
    )
    #se ingresa un id que no existe para ningun usuario
    respuesta = get_usuario_autenticado.post('/api/usuarios/0000/modificar_saldo/', {
        'monto': 500,
        'codigo': 'RECARGA_SALDO12456'
    })

    assert respuesta.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_saldo_insuficiente(get_usuario):

    try:
        get_usuario.saldo= Decimal(15000)
        get_usuario.save()
        comprobar_saldo(get_usuario,Decimal(20000))

    except SaldoInsuficienteException as e:
        assert 'Saldo insuficinte para realizar esta accción' == str(e)