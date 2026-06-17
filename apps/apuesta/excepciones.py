
class NoExistenPartidosError(Exception):
    def __str__(self):
        return "No existen partidos en el rango de fecha proporcionado"

class FechasError(Exception):
    def __str__(self):
        return "Error en las fechas ingresadas,por favor revisar"
