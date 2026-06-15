import pytest
from apps.apuesta.models import Partido

@pytest.fixture
def get_partido():

    return Partido.objects.create(
        equipo_local="River",
        equipo_visitante="Boca",
        estado="pendiente"
    )