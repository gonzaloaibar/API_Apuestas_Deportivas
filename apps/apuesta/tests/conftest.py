# conftest.py
import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.usuario.tests.fixture_usuario import crear_usuario
from apps.apuesta.models import Partido, OpcionApuesta, Apuesta, ResultadoPartido, TipoApuesta, Prediccion



### FIXTURES DE PARTIDO

@pytest.fixture
def get_partido(db):
    #partido pendiente
    return Partido.objects.create(
        api_football_id=99999,
        equipo_local="Boca Juniors",
        equipo_visitante="River Plate",
        goles_local=None,
        goles_visitante=None,
        resultado_partido=ResultadoPartido.LOCAL,   # valor requerido por el modelo
        estado="pendiente",
        fecha=timezone.now() + timezone.timedelta(days=1),
    )

@pytest.fixture
def get_partido_finalizado(db):
    #partido jugado con el resultado incluido
    return Partido.objects.create(
        api_football_id=88888,
        equipo_local="Boca Juniors",
        equipo_visitante="River Plate",
        goles_local=2,
        goles_visitante=1,
        resultado_partido=ResultadoPartido.LOCAL,
        estado="finalizado",
        fecha=timezone.now() - timezone.timedelta(days=1),
    )


### FIXTURES PARA OPCIONES DE APUESTA

@pytest.fixture
def opcion_apuesta(get_partido):
    return OpcionApuesta.objects.create(
        partido=get_partido,
        tipo_apuesta=TipoApuesta.RESULTADO,
        prediccion=Prediccion.GANA_VISITANTE,
        multiplicador=Decimal("1.80"),
        monto_minimo=Decimal("100.00"),
    )

@pytest.fixture
def opcion_resultado_local(get_partido):
    #opcion de apuesta para gana local
    return OpcionApuesta.objects.create(
        partido=get_partido,
        tipo_apuesta=TipoApuesta.RESULTADO,
        prediccion=Prediccion.GANA_LOCAL,
        multiplicador=Decimal("1.80"),
        monto_minimo=Decimal("100.00"),
    )

@pytest.fixture
def opcion_apuesta_partido_finalizado(get_partido_finalizado):
    #opcion de apuesta para gana local
    return OpcionApuesta.objects.create(
        partido=get_partido_finalizado,
        tipo_apuesta=TipoApuesta.RESULTADO,
        prediccion=Prediccion.GANA_LOCAL,
        multiplicador=Decimal("1.80"),
        monto_minimo=Decimal("100.00"),
    )

@pytest.fixture
def get_opcion_goles(get_partido):
    #opcion de apuesta para mas de tres goles
    return OpcionApuesta.objects.create(
        partido=get_partido,
        tipo_apuesta=TipoApuesta.GOLES,
        prediccion=Prediccion.MAS_3_GOLES,
        multiplicador=Decimal("2.50"),
        monto_minimo=Decimal("500.00"),
    )


### FIXTURES PARA APUESTA

@pytest.fixture
def get_apuesta_pendiente(get_usuario_cliente, opcion_resultado_local):
    #apuesta en estado pendiente sin resolver
    return Apuesta.objects.create(
        apostado_por=get_usuario_cliente,
        opcion_apuesta=opcion_resultado_local,
        monto_apostado=Decimal("500.00"),
        estado="pendiente",
        ganancia_cliente=Decimal("0.00"),
        ganancia_casa=Decimal("0.00"),
    )

@pytest.fixture
def get_apuesta_ganada(get_usuario_cliente, opcion_resultado_local):
    #apuesta en estado ganada resuelta
    monto = Decimal("500.00")
    multiplicador = opcion_resultado_local.multiplicador       # 1.80
    ganancia = (monto * multiplicador).quantize(Decimal("0.01"))
    return Apuesta.objects.create(
        apostado_por=get_usuario_cliente,
        opcion_apuesta=opcion_resultado_local,
        monto_apostado=monto,
        estado="ganada",
        ganancia_cliente=ganancia,    # 900.00
        ganancia_casa=Decimal("0.00"),
    )

@pytest.fixture
def get_apuesta_perdida(get_usuario_cliente, opcion_resultado_local):
    #apuesta en estado perdida resuelta
    monto = Decimal("500.00")
    return Apuesta.objects.create(
        apostado_por=get_usuario_cliente,
        opcion_apuesta=opcion_resultado_local,
        monto_apostado=monto,
        estado="perdida",
        ganancia_cliente=Decimal("0.00"),
        ganancia_casa=monto,          # la casa se queda con lo apostado
    )


### PARA TEST QUE NECESITAN MULTIPLES APUESTAS

@pytest.fixture
def crear_apuesta(get_usuario_cliente, opcion_resultado_local):

    def _crear(
        apostado_por=None,
        opcion_apuesta=None,
        monto_apostado=Decimal("200.00"),
        estado="pendiente",
        ganancia_cliente=Decimal("0.00"),
        ganancia_casa=Decimal("0.00"),
    ):
        return Apuesta.objects.create(
            apostado_por=apostado_por or get_usuario_cliente,
            opcion_apuesta=opcion_apuesta or opcion_resultado_local,
            monto_apostado=monto_apostado,
            estado=estado,
            ganancia_cliente=ganancia_cliente,
            ganancia_casa=ganancia_casa,
        )
    return _crear