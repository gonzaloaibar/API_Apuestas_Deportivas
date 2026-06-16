import pytest
from apps.apuesta.models import Partido

@pytest.fixture
def crear_partidos():
    def _crear(api_football_id,
       equipo_local,
       equipo_visitante,
       estado,
       fecha
    ):
        return Partido.objects.create(
            api_football_id = api_football_id,
            equipo_local = equipo_local,
            equipo_visitante = equipo_visitante,
            estado = estado,
            fecha = fecha,
        )

    #retornar la funcion me va a permitir crear varios partidos
    return _crear

@pytest.fixture
def get_partido():

    return Partido.objects.create(
        api_football_id = "123738",
        equipo_local="River",
        equipo_visitante="Boca",
        estado="pendiente"
    )

@pytest.fixture
def get_partido_finalizado():

    return Partido.objects.create(
        api_football_id = "123738",
        equipo_local="River",
        equipo_visitante="Boca",
        estado="finalizado"
    )