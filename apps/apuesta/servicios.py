from django.utils.dateparse import parse_datetime
from django.conf import settings
from datetime import datetime
from django.utils import timezone

#Al tener la opcion de que la fehca se ingrese por el punto .env
# se deben tener en cuanta que el usuario puede ingresar un formato diferente
# al que maneja el JSON y la BD, por lo tanto se parsea la fecha
def parsear_fecha(fecha):
    if fecha is None:
        raise ValueError("La fecha no puede ser None")

    if isinstance(fecha, datetime):
        if timezone.is_naive(fecha):
            return timezone.make_aware(fecha)
        return fecha

    if isinstance(fecha, str):
        #porque el usuario en el .env puede ingresar mal la fecha
        formatos = [
            "%Y-%m-%dT%H:%M:%S%z",  # 2023-01-26T22:15:00+00:00
            "%Y-%m-%dT%H:%M:%S",    # 2023-05-20T20:00:00
            "%Y-%m-%d %H:%M:%S",    # 2023-05-20 20:00:00
            "%Y-%m-%d",             # 2023-05-20
            "%d/%m/%Y %H:%M:%S",    # 20/05/2023 20:00:00
            "%d/%m/%Y",             # 20/05/2023
        ]
        for formato in formatos:
            try:
                fecha_dt = datetime.strptime(fecha, formato)
                # Si ya tiene timezone no hace falta make_aware
                if timezone.is_naive(fecha_dt):
                    return timezone.make_aware(fecha_dt)
                return fecha_dt
            except ValueError:
                continue

        raise ValueError(f"Formato de fecha no reconocido: {fecha}")

    raise TypeError(f"Tipo no soportado: {type(fecha)}")

#Esta funcion nos va a servir para simular la fecha desde una vvariable de entorno
#como la variable no se sube al gtihub entonces devuelvo la fecha actual
#pero para que funcione la api completamente se deberia tener la version premium de
#APIFootball
def obtener_fecha_actual():
    fecha_simulada = getattr(settings, "FECHA_SIMULADA", None)
    fecha_simulada = parsear_fecha(fecha_simulada)

    if fecha_simulada:
        return fecha_simulada

    return datetime.now() #si no hay fecha simulada saca la fecha actual del sistema

def fecha_1_mayor_fecha_2(fecha_1,fecha_2):
    fecha_1 = parsear_fecha(fecha_1)
    fecha_2 = parsear_fecha(fecha_2)
    if fecha_1 > fecha_2:
        return True
    else:
        return False
