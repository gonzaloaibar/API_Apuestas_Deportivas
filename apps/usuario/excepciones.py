from rest_framework.exceptions import APIException
from rest_framework import status

class SaldoInsuficienteException(APIException):
    codigo = status.HTTP_400_BAD_REQUEST
    default_detail = 'Saldo insuficinte para realizar esta accción'
    default_code = 'Saldo insuficiente'

