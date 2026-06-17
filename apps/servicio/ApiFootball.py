import requests
from django.conf import settings
from django.http import JsonResponse

from apps.apuesta.excepciones import NoExistenPartidosError, FechasError
from apps.apuesta.models import Partido
from apps.apuesta.servicios import fecha_1_mayor_fecha_2, obtener_fecha_actual


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
    fecha_simulada = obtener_fecha_actual()

    if fecha_1_mayor_fecha_2(fecha_simulada,fecha_partido):
        return 'finalizado'
    else:
        return 'pendiente'

class APIFootballService:
    @staticmethod
    def importar(fecha_inicio, fecha_fin):
        if fecha_1_mayor_fecha_2(fecha_inicio, fecha_fin):
            raise FechasError (f'La fecha {fecha_inicio} es posterior a la fecha {fecha_fin}, por favor revise')
        url = 'https://v3.football.api-sports.io/fixtures'
        headers = {
            'x-apisports-key': settings.API_FOOTBALL_KEY
        }
        params = {
            'league': 128,  # por el momento solo liga argentina
            'season': 2023,
            'from': fecha_inicio,
            'to': fecha_fin
        }
        response = requests.get(
            url,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        if data.get("results") == 0:
            raise NoExistenPartidosError #ValueError("No existen partidos en el rango de fecha proporcionado")

        if data.get("errors"):
            raise ValueError(
                f"API Football: {data['errors']}"
            )

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

        return partidos_creados