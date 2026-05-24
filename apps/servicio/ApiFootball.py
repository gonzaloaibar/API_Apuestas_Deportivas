import requests
from django.conf import settings
from apps.apuesta.models import Partido

class APIFootballService:
    @staticmethod
    def importar(from_date, to_date):


        url = 'https://v3.football.api-sports.io/fixtures'

        headers = {
            'x-apisports-key': settings.API_FOOTBALL_KEY
        }

        params = {
            'league': 128,  # por el momento solo liga argentina
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

        for item in data['response']:
            fixture = item['fixture']
            teams = item['teams']
            goals = item['goals']

            _, created = Partido.objects.get_or_create(
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

