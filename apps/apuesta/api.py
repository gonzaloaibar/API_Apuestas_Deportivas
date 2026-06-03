from contourpy import contour_generator
from django.db import transaction
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status,filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, DjangoModelPermissions
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
from dotenv import dotenv_values

from ..usuario.permissions import EsPropietarioApuesta, EsAdministrador


class PartidoViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated & DjangoModelPermissions]

    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['estado','fecha']

    @action(methods=['post'], detail=False)
    def importar_partidos(self, request):
        print("ENTRO AL ENDPOINT")
        fecha_desde = request.data.get('from')
        fecha_hasta = request.data.get('to')

        try:
            APIFootballService.importar(fecha_desde, fecha_hasta)

        except Exception as e:
            return Response({'error':e})

        return Response({'mensaje': 'se importo correctamente los partidos'},status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def terminar_partido(self, request):

        partidos = Partido.objects.filter(estado='pendiente')

        #comprueba un cambio en la fecha simulada
        config = dotenv_values(".env")
        fecha_simulada = config.get('FECHA_HORA_SIMULADA')

        try:
            for partido  in partidos:
                if fecha_1_mayor_fecha_2(fecha_simulada,partido.fecha):
                    resolver_apuesta(partido.pk)
                    partido.estado = "finalizado"
                    partido.save()
            #partido=self.get_object()
        except ValueError:
            return Response({'error':'Error en la fecha'},status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"resultado":f"partidos terminados", "mensaje":"Apuestas ejecutadas correctamente"},status=HTTP_200_OK)

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
        #Porque un usuario sin cuenta podria querer ver que onda con la aplicacion
        permission_classes = [IsAuthenticated & DjangoModelPermissions]
        filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
        ordering_fields = ['estado', 'fecha','partido']
        queryset = OpcionApuesta.objects.all()
        serializer_class = OpcionApuestaSerializer

def comprobar_saldo(Usuario,monto_apostado):
    if Usuario.saldo < monto_apostado:
        raise SaldoInsuficienteException()

class ApuestaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, EsPropietarioApuesta]
    queryset = Apuesta.objects.all()

    #filtrar apuestas por usuario
    def get_queryset(self):
        return Apuesta.objects.filter(
            apostado_por=self.request.user
        )
    serializer_class = ApuestaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['estado', 'fecha']

    def perform_create(self, serializer):

        usuario = Usuario.objects.get(id=self.request.user.id)

        monto_apostado = serializer.validated_data['monto_apostado']
        comprobar_saldo(usuario,monto_apostado)
        usuario.saldo -= monto_apostado

        usuario.save()

        serializer.save(apostado_por=usuario)


    @action(methods={'delete'},detail=True)
    def eliminar_apuesta(self,request,pk=None):
        apuesta = self.get_object()

        # if request.user.id != apuesta.apostado_por.id:
        #     return Response(
        #         {'ERROR':'No puede eliminar una apuesta que usted no realizo'},
        #         status=status.HTTP_403_FORBIDDEN)
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

        if fecha_1_mayor_fecha_2(fecha_partido, fecha_simulada):
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
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, EsAdministrador]
    )
    def ganancias_casa(self, request):

        total_apostado = (
                Apuesta.objects.aggregate(
                    total=Sum("monto_apostado")
                )["total"] or 0
        )

        total_pagado = (
                Apuesta.objects.aggregate(
                    total=Sum("ganancia_cliente")
                )["total"] or 0
        )

        ganancia_real = total_apostado - total_pagado

        return Response({
            "total_apostado": total_apostado,
            "premios_pagados": total_pagado,
            "ganancia_real_casa": ganancia_real
        })