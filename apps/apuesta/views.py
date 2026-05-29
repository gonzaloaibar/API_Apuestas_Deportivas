from urllib.error import HTTPError

import requests

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Model

from rest_framework import status, response
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import Partido, Apuesta, OpcionApuesta
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
        return Response({'mensaje': 'funciona'},status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True)
    def terminar_partido(self, request, pk=None):
        partido=self.get_object()
        print(partido)
        partido.estado="finalizado"


        #resolver_apuesta(partido.pk, partido.resultado_partido)
        partido.save()
        return Response({"estado":"partido terminado"})

# def resolver_apuesta_resultado():
#     print("resolver_resultado")
#     pass
#
# def resolver_apuesta_goles():
#     print("goles")
#     pass
#
#
# def resolver_apuesta(id_partido, resultado_partido):
#
#     apuestas=Apuesta.objects.filter(partido=id_partido)
#     print(apuestas)
#     for apuesta in apuestas:
#         tipo=TipoApuesta.objects.get(nombre=apuesta.tipo_apuesta)
#         print(tipo)
#         if tipo.pk == 1:
#             resolver_apuesta_resultado()
#         elif tipo.pk == 2:
#             resolver_apuesta_goles()


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
