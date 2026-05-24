import requests

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import Partido, Apuesta
from .serializers import PartidoSerializer

class PartidoViewSet(ModelViewSet):

    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer

    # @action(detail=False, methods=['post'])
    # def importar(self, request):
    #     return Response({
    #         'mensaje': 'Funciona'
    #     })

    @action(methods=['post'], detail=False)
    def importar(self, request):
        from_date=request.data.get('from')
        to_date=request.data.get('to')

        if not from_date or not to_date:
            return Response(
                {
                    'error': 'Debe enviar from y to'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        url='https://v3.football.api-sports.io/fixtures'

        headers = {
            'x-apisports-key': settings.API_FOOTBALL_KEY
        }

        params = {
            'league': 128,
            'season': 2023,
            'from': from_date,
            'to': to_date
        }

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        data = response.json()

        partidos_creados = 0

        print(response.status_code)
        print(data)
        print(len(data['response']))

        for item  in data['response']:
            fixture = item['fixture']
            teams = item['teams']
            goals = item['goals']

            _, created=Partido.objects.get_or_create(
                api_football_id=fixture['id'],
                defaults={
                    'equipo_local': teams['home']['name'],
                    'equipo_visitante': teams['away']['name'],
                    'fecha': fixture['date'],
                    'goles_local': goals['home'],
                    'goles_visitante': goals['away'],
                    'estado': 'pendiente',
                    'resultado_partido': True
                }
            )
            print(item)
            if created:
                partidos_creados += 1

        return Response(
            {
                'mensaje': 'Importación completada',
                'partidos creados': partidos_creados
            },
            status=status.HTTP_200_OK
        )