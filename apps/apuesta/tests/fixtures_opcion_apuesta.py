import pytest
from apps.apuesta.models import OpcionApuesta,Partido
from .fixtures_partido import get_partido

@pytest.fixture
def crear_opcion_apuesta(get_partido):

    opcion_apuesta, _ = OpcionApuesta.objects.get_or_create(
        partido = get_partido,
        tipo_apuesta = 'resultado',
        prediccion = 'empate',
        multiplicador = 2.5,
        monto_minimo = 5000
    )

    return opcion_apuesta


@pytest.fixture
def get_opcion_apuesta(get_partido):

    return OpcionApuesta.objects.create(
        partido=get_partido,
        tipo_apuesta="resultado",
        prediccion="gana_local",
        multiplicador=1.9,
        monto_minimo=1000
    )