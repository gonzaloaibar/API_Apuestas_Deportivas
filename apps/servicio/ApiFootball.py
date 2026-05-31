import requests
from django.conf import settings
from apps.apuesta.models import Partido

def definir_resultado_partido(estado_de_partido,goles_local,goles_visitante):
    # if fixture['status']['short'] != 'FT':
    #     #DOCUMENTAR:
    #     # "FT" es el parametro de partido finalizado, como son partidos viejos es el item que nos importa
    #     #de otro modo el partido fue cancelado, suspendido o resuelto por mesa
    #     #por lo tanto lo tomamos como cancelado para este ejemplo
    #     resultado = 'C'
    # elif item['goals']['home'] > item['goals']['away']:
    #     resultado = 'L'
    # elif item['goals']['home'] < item['goals']['away']:
    #     resultado = 'v'
    # else:
    #     #Caso de empate
    #     resultado = 'E'
    if estado_de_partido != 'FT':
        return 'C'
    elif goles_local > goles_visitante:
        return 'L'
    elif goles_local < goles_visitante:
        return 'V'
    else:
        return 'E'

#Vamos a comparar la fecha del partido con la fecha simuladada
def definir_estado(fecha_partido):
    fecha_simulada = getattr(settings, "FECHA_SIMULADA", None)
    if fecha_partido < fecha_simulada:
        return 'finalizado'
    else:
        return 'pendiente'

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
                    'estado': definir_estado(fixture['date']),
                    'resultado_partido': definir_resultado_partido(fixture['status']['short'],item['goals']['home'],item['goals']['away'])
                }
            )

            if created:
                partidos_creados += 1

