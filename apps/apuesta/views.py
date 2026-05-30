from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import Partido, Apuesta, OpcionApuesta, TipoApuesta, Prediccion
from .serializers import PartidoSerializer, ApuestaSerializer, OpcionApuestaSerializer

from apps.servicio.ApiFootball import APIFootballService
from ..usuario.models import Usuario


class PartidoViewSet(ModelViewSet):

    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer

    # @action(detail=False, methods=['post'])
    # def importar(self, request):
    #     return Response({
    #         'mensaje': 'Funciona'
    #     })

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
    print(f'PARTIDO RESOLVER APUESTA POR RESULTADO {partido}')

    #comparo el resultado del partido y la prediccion que figura en la apuesta
    #si el usuario acerto debo traerlo y agregar a su saldo el premio de la apuesta
    #caso contrario toodo va para la casa de apuestas
    if opcion_apuesta.prediccion == partido.resultado_partido:
        print(f'tipo de apuesta: {opcion_apuesta.tipo_apuesta}')
        cliente = apuesta.apostado_por
        print(f'cliente: {cliente.username}')
        ## --> considero que la forma mas realista de hacerlo es que la casa se quede un porcentaje del premio
        #porque supongo que asi funcionan las casas de apuestas ellos ganan siempre
        premio = apuesta.monto_apostado * opcion_apuesta.multiplicador
        apuesta.ganancia_cliente = premio

        print(f'Ganania del cliente: {apuesta.ganancia_cliente}')
        #le agrego el saldo al cliente
        cliente.saldo += apuesta.ganancia_cliente
        print(f'nuevo saldo del cliente: {cliente.saldo}')
        cliente.save()
        #cambio el estado de la apuesta
        apuesta.estado = 'ganada'
        apuesta.save()
    else:
        apuesta.ganancia_casa = apuesta.monto_apostado
        print(f"ganancia de la casa {apuesta.ganancia_casa}")
        apuesta.estado = "perdida"
        apuesta.save()

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
        # else:
        #     #Aca se deberia ampliar la logica para los otros tipos de apuestas
        #     print(f'La apuesta no es por resultado es por {opcion.tipo_apuesta}')
        elif opcion.tipo_apuesta == TipoApuesta.GOLES:
            resolver_apuesta_goles(apuesta,opcion)



class OpcionApuestaViewSet(ModelViewSet):
        queryset = OpcionApuesta.objects.all()
        serializer_class = OpcionApuestaSerializer

class ApuestaViewSet(ModelViewSet):
    queryset = Apuesta.objects.all()
    serializer_class = ApuestaSerializer

    def perform_create(self, serializer):

        if serializer.is_valid():
            usuario = Usuario.objects.get(id=1)
            serializer.save(apostado_por=usuario)

            return Response({"data":"guardado"},status=HTTP_200_OK)
        return Response(serializer.error,status=HTTP_400_BAD_REQUEST)
