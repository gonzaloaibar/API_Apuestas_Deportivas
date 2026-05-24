
import requests

from django.conf import settings

from rest_framework import status, response
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import Partido, Apuesta
from .serializers import PartidoSerializer, ApuestaSerializer

from apps.servicio.ApiFootball import APIFootballService

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
        print(request.data)
        fecha_desde = request.data.get('from')
        fecha_hasta = request.data.get('to')
        APIFootballService.importar(fecha_desde, fecha_hasta)
        return Response({'mensaje': 'funciona'},status=status.HTTP_200_OK)

class ApuestaViewSet(ModelViewSet):
    queryset = Apuesta.objects.all()
    serializer_class = ApuestaSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
