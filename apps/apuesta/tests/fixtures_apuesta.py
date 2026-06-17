import pytest

from apps.apuesta.models import Apuesta
from .fixtures_opcion_apuesta import*
from apps.usuario.tests.fixture_usuario import*

@pytest.fixture
def get_apuesta(get_usuario_autenticado, get_opcion_apuesta):

    return Apuesta.objects.create(
        apostado_por=get_usuario_autenticado,
        opcion_apuesta=get_opcion_apuesta,
        monto_apostado=5000
    )

