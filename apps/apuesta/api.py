from decimal import Decimal
import requests
from decouple import config
from django.db import transaction
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status,filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .excepciones import NoExistenPartidosError, FechasError
from .filters import PartidoFilter
from .models import Partido, Apuesta, OpcionApuesta, TipoApuesta, Prediccion
from .serializers import PartidoSerializer, ApuestaSerializer, OpcionApuestaSerializer, ModificarApuestaSerializer
from .servicios import fecha_1_mayor_fecha_2, obtener_fecha_actual

from apps.servicio.ApiFootball import APIFootballService
from ..usuario.models import Usuario
from ..usuario.excepciones import SaldoInsuficienteException
from dotenv import dotenv_values

from ..usuario.permissions import EsPropietarioApuesta, EsAdministrador
from django.db import transaction

class PartidoViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated & DjangoModelPermissions]

    queryset = Partido.objects.all().order_by('fecha')
    lookup_field = 'uuid'
    serializer_class = PartidoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PartidoFilter
    ordering_fields = ['estado','fecha']

    filterset_fields = {
        "fecha": ["gte", "lte"]
    }

    @action(methods=['post'], detail=False)
    def importar_partidos(self, request):

        fecha_desde = request.data.get('from')
        fecha_hasta = request.data.get('to')

        if not fecha_desde or not fecha_hasta:
            return Response(
                {'error': 'Los campos from y to son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            partidos_creados = APIFootballService.importar(fecha_desde, fecha_hasta)
            if partidos_creados > 0:
                return Response({'mensaje': f'se importaron correctamente {partidos_creados} partidos'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'mensaje': f'El rango de fechas que ingreso corresponde a partidos que ya estan cargados'},
                    status=status.HTTP_200_OK)

        except NoExistenPartidosError as no_partidos:
            return Response({'error': f'{no_partidos.__str__()}'},status=status.HTTP_404_NOT_FOUND)
        except FechasError as error_fechas:
            return Response({'error': f'{error_fechas}'},status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.HTTPError as http_err:

            return Response({"error": "Hubo un problema al consultar el servicio externo."}, status=status.HTTP_502_BAD_GATEWAY)

        except requests.exceptions.ConnectionError as conn_err:

            return Response({"error": "No se pudo conectar al servicio externo. Inténtelo más tarde."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except requests.exceptions.Timeout as timeout_err:

            return Response({"error": "El servicio externo tardó demasiado en responder."}, status=status.HTTP_504_GATEWAY_TIMEOUT)

        except ValueError as e:
            return Response(
                {'error': f'{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(methods=['patch'], detail=False)
    def terminar_partido(self, request):

        partidos = Partido.objects.filter(estado='pendiente')

        #comprueba un cambio en la fecha simulada
        config = dotenv_values(".env")
        fecha_simulada = config.get('FECHA_HORA_SIMULADA')

        try:
            for partido  in partidos:
                if fecha_1_mayor_fecha_2(fecha_simulada,partido.fecha):
                    resolver_apuesta(partido.id)
                    partido.estado = "finalizado"
                    partido.save()
            #partido=self.get_object()
        except ValueError:
            return Response({'error':'Error en la fecha'},status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"resultado":f"partidos terminados", "mensaje":"Apuestas ejecutadas correctamente"},status=status.HTTP_200_OK)

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
    PORCENTAJE_DE_COMISION = Decimal(str(dotenv_values(".env").get("PORCENTAJE_DE_COMISION")))

    cliente = apuesta.apostado_por
    #Calculo para definir la ganancia de la casa, la cual se llevara un porcentaje expecificado en el archivo .env
    premio_parcial = apuesta.monto_apostado * opcion_apuesta.multiplicador
    ganancia = premio_parcial - apuesta.monto_apostado
    comision = ganancia * PORCENTAJE_DE_COMISION

    premio_final = premio_parcial - comision

    apuesta.ganancia_cliente = premio_final
    apuesta.ganancia_casa = comision

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
        filterset_fields = {
            "multiplicador": ["gte", "lte"]
        }
        queryset = OpcionApuesta.objects.all()
        lookup_field = 'uuid'
        serializer_class = OpcionApuestaSerializer

def comprobar_saldo(Usuario,monto_apostado):
    if Usuario.saldo < monto_apostado:
        raise SaldoInsuficienteException()

class ApuestaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, EsPropietarioApuesta]
    queryset = Apuesta.objects.all()
    lookup_field = 'uuid'

    #filtrar apuestas por usuario
    def get_queryset(self):
        return Apuesta.objects.filter(
            apostado_por=self.request.user
        )
    serializer_class = ApuestaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['estado', 'fecha']
    filterset_fields = ["estado"]

    def perform_create(self, serializer):

        usuario = Usuario.objects.get(id=self.request.user.id)

        monto_apostado = serializer.validated_data['monto_apostado']
        comprobar_saldo(usuario,monto_apostado)
        usuario.saldo -= monto_apostado

        usuario.save()

        serializer.save(apostado_por=usuario)

    @action(methods=["patch"], detail=True)
    def modificar_apuesta(self, request, uuid=None):

        apuesta=self.get_object() #obtengo la apuesta
        serializer = ModificarApuestaSerializer(instance=apuesta, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        nuevo_monto = request.data.get("monto_apostado")#obtengo el nuevo monto de la request, si viene
        nueva_opcion_uuid = request.data.get("opcion_apuesta")#obtengo la nueva opcion de la request, si viene
        usuario = request.user#obtengo el usuario que realizo la request

        #valido que se envien el o los campos para la modificacion
        if not request.data:
            return Response(
                {
                    "error":
                        "Debe indicar al menos un campo a modificar."
                },
                status=400
            )

        #pregunto si nuevo monto vino en la request o es None
        nuevo_monto = (
            Decimal(str(nuevo_monto))
            if nuevo_monto is not None
            else apuesta.monto_apostado
        )

        #si nueva_opcion no es None hago la modificacion
        if nueva_opcion_uuid:

            #ahora la nueva opcion reemplaza la anterior
            nueva_opcion = OpcionApuesta.objects.get(
                uuid=nueva_opcion_uuid
            )

        else:
            #caso contrario no se esta modificando la opcion, conserva la actual
            nueva_opcion = apuesta.opcion_apuesta

        #realizar la modificacion en el monto
        monto_actual = apuesta.monto_apostado

        diferencia = nuevo_monto - monto_actual

        if diferencia > 0:
            if usuario.saldo < diferencia:
                return Response(
                    {
                        "error": (
                            "Saldo insuficiente para "
                            "aumentar la apuesta."
                        )
                    },
                    status=400
                )
            usuario.saldo -= diferencia

        elif diferencia < 0:
            usuario.saldo += abs(diferencia)



        apuesta.monto_apostado = nuevo_monto
        apuesta.opcion_apuesta = nueva_opcion

        with transaction.atomic():
            usuario.save()
            apuesta.save()

        return Response(
            {
                "mensaje": "Apuesta modificada."

            }
        )



    @action(methods={"delete"},detail=True,
            permission_classes=[IsAuthenticated, EsPropietarioApuesta])
    def eliminar_apuesta(self,request,uuid=None):
        apuesta = self.get_object()
        print("entro al metodo")
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

        if fecha_1_mayor_fecha_2(fecha_simulada, fecha_partido):
            return Response(
                {'error': f'No se puede eliminar la apuesta {uuid}, el partido ya comenzó.'},
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