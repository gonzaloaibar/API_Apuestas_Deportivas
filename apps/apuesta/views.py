from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status,filters
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import Partido, Apuesta, OpcionApuesta, TipoApuesta, Prediccion
from .serializers import PartidoSerializer, ApuestaSerializer, OpcionApuestaSerializer
from .servicios import fecha_1_mayor_fecha_2, obtener_fecha_actual

from apps.servicio.ApiFootball import APIFootballService
from ..usuario.models import Usuario
from ..usuario.excepciones import SaldoInsuficienteException


class PartidoViewSet(ModelViewSet):

    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['estado','fecha']

    @action(methods=['post'], detail=False)
    def importar_partidos(self, request):

        fecha_desde = request.data.get('from')
        fecha_hasta = request.data.get('to')
        APIFootballService.importar(fecha_desde, fecha_hasta)

        return Response({'mensaje': 'se importo correctamente los partidos'},status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True)
    def terminar_partido(self, request, pk=None):
        partido=self.get_object()
        print(partido.resultado_partido)


        resolver_apuesta(partido.pk)

        partido.estado = "finalizado"
        partido.save()

        return Response({"resultado":f"partido {partido} terminado", "mensaje":"Apuestas ejecutadas correctamente"},status=HTTP_200_OK)

@transaction.atomic
def resolver_apuesta_resultado(apuesta,opcion_apuesta):
    #necesito el partido
    partido = opcion_apuesta.partido

    if opcion_apuesta.prediccion == partido.resultado_partido:
        resolver_apuesta_ganada(apuesta,opcion_apuesta)
    else:
        resolver_apuesta_perdida(apuesta)

#comparo el resultado del partido y la prediccion que figura en la apuesta
#si el usuario acerto debo traerlo y agregar a su saldo el premio de la apuesta
#caso contrario toodo va para la casa de apuestas
def resolver_apuesta_ganada(apuesta, opcion_apuesta):
    cliente = apuesta.apostado_por

    premio = apuesta.monto_apostado * opcion_apuesta.multiplicador
    apuesta.ganancia_cliente = premio

    cliente.saldo += apuesta.ganancia_cliente

    cliente.save()
    # cambio el estado de la apuesta
    apuesta.estado = 'ganada'
    apuesta.save()


def resolver_apuesta_perdida(apuesta):
    apuesta.ganancia_casa = apuesta.monto_apostado

    apuesta.estado = "perdida"
    apuesta.save()

def resolver_apuesta_goles(apuesta, opcion_apuesta):
    partido = opcion_apuesta.partido
    goles_totales = partido.goles_local + partido.goles_visitante

    prediccion = opcion_apuesta.prediccion
    acierto = False

    if prediccion == Prediccion.MAS_1_GOL:
        acierto = goles_totales > 1
    if prediccion == Prediccion.MAS_3_GOLES:
        acierto = goles_totales >3
    if prediccion == Prediccion.MAS_5_GOLES:
        acierto = goles_totales > 5

    if acierto:
        resolver_apuesta_ganada(apuesta, opcion_apuesta)
    else:
        resolver_apuesta_perdida(apuesta)


def resolver_apuesta(id_partido):
    apuestas=(
        Apuesta.objects.filter(
            opcion_apuesta__partido=id_partido,
            estado="pendiente"
        ).select_related(#optimizador de consultas de django
            "opcion_apuesta",
            "opcion_apuesta__partido"
        )
    )

    for apuesta in apuestas:

        opcion = apuesta.opcion_apuesta

        if opcion.tipo_apuesta == TipoApuesta.RESULTADO:
            resolver_apuesta_resultado(apuesta,opcion)

        elif opcion.tipo_apuesta == TipoApuesta.GOLES:
            resolver_apuesta_goles(apuesta,opcion)


class OpcionApuestaViewSet(ModelViewSet):
        queryset = OpcionApuesta.objects.all()
        serializer_class = OpcionApuestaSerializer

def comprobar_saldo(Usuario,monto_apostado):
    if Usuario.saldo < monto_apostado:
        raise SaldoInsuficienteException()

class ApuestaViewSet(ModelViewSet):
    queryset = Apuesta.objects.all()
    serializer_class = ApuestaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['estado', 'fecha']

    def perform_create(self, serializer):
        usuario = Usuario.objects.get(id=1)

        monto_apostado = serializer.validated_data['monto_apostado']
        comprobar_saldo(usuario,monto_apostado)
        usuario.saldo -= monto_apostado

        usuario.save()

        serializer.save(apostado_por=usuario)


    @action(methods={'delete'},detail=True)
    def eliminar_apuesta(self,request,pk=None):
        apuesta = self.get_object()

        if apuesta.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden eliminar apuestas pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        #la fecha simulada se debe normalizar porque es un string
        #si la vamos a comparar con objectos que vienen de la BD tenemos que hacerlo
        #se puede armar una funcion extra si hay tiempo
        fecha_simulada = obtener_fecha_actual()
        fecha_partido = apuesta.opcion_apuesta.partido.fecha

        if fecha_1_mayor_fecha_2(fecha_simulada, fecha_partido):
            return Response(
                {'error': f'No se puede eliminar la apuesta {pk}, el partido ya comenzó.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        #Al usuario se le devuelve el monto apostado,
        #se va a tener que controlas y aclarar si es que la casa se queda un porcentaje
        usuario = apuesta.apostado_por
        usuario.saldo += apuesta.monto_apostado
        usuario.save()
        apuesta.delete()

        return Response(
            {'mensaje': 'Apuesta eliminada correctamente.'},
            status=status.HTTP_204_NO_CONTENT
        )