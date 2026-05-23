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
