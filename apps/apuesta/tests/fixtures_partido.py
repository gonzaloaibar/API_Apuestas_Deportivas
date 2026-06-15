import pytest
from apps.apuesta.models import Partido

@pytest.fixture
def get_partido():

    return Partido.objects.create(
        api_football_id = "123738",
        equipo_local="River",
        equipo_visitante="Boca",
        estado="pendiente"
    )