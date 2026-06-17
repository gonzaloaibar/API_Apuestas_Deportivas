import pytest
from apps.apuesta.models import OpcionApuesta
from .fixtures_partido import* #get_partido


@pytest.fixture
def get_opcion_apuesta(get_partido):

    return OpcionApuesta.objects.create(
        partido=get_partido,
        tipo_apuesta="resultado",
        prediccion="gana_local",
        multiplicador=1.9,
        monto_minimo=1000
    )