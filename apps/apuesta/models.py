from django.db import models

# Create your models here.
class Partido(models.Model):

    equipo_local = models.CharField()
    equipo_visitante = models.CharField()
    goles_local = models.IntegerField()
    goles_visitante = models.IntegerField()
    resultado_partido = models.IntegerField()
    tarjetas_amarillas = models.IntegerField()
    tarjetas_rojas = models.IntegerField()
    estado = models.CharField()
    id_apifootball = models.CharField()
    fecha = models.DateTimeField() #posiblemente se pueda usar null

class TipoApuesta(models.Model):

    nombre = models.CharField(max_length=100)
    multiplicador = models.DecimalField(max_digits=5, decimal_places=2)
    monto_minimo = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.nombre},{self.multiplicador}, {self.multiplicador}'


class Apuesta(models.Model):
    ESTADOS = (
        ("pendiente", "Pendiente"),
        ("ganada", "Ganada"),
        ("perdida", "Perdida"),
    )

    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    tipo_apuesta = models.ForeignKey(TipoApuesta, on_delete=models.CASCADE)
    monto_apostado= models.DecimalField(max_digits=5, decimal_places=2)
    prediccion = models.CharField(max_length=100)
    cuota_aplicada = models.DecimalField(max_digits=5, decimal_places=2)
    estado = models.CharField(default="pendiente", max_length=100, choices=ESTADOS)
    ganancia_cliente = models.DecimalField(max_digits=5, decimal_places=2)
    ganancia_casa = models.DecimalField(max_digits=5, decimal_places=2)
    resultado_apuesta = models.CharField(max_length=100)
    fecha = models.DateTimeField()

    def __str__(self):
        return f'{self.tipo_apuesta.nombre},{self.partido},{self.estado},{self.ganancia_casa},{self.fecha}'
