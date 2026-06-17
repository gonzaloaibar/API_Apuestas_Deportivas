
class NoExistenPartidosError(Exception):
    def __str__(self):
        return "No existen partidos en el rango de fecha proporcionado"