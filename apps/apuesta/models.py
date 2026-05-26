from django.db import models

#ESTOS SON LOS POSIBLES RESULTADOS DE UN PARTIDO, POR LO TANTO SE MANEJARAN COMO CONSTANTES
class ResultadoPartido(models.TextChoices):
    LOCAL = "L", "Gana Local"
    EMPATE = "E", "Empate"
    VISITANTE = "V", "Gana Visitante"
    CANCELADO =  "C", "El partido se canceló por algún motivo externo"

class Partido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('finalizado', 'Finalizado'),
    )
    api_football_id = models.IntegerField(unique=True)
    equipo_local = models.CharField(max_length=100)
    equipo_visitante = models.CharField(max_length=100)
    goles_local = models.IntegerField(null=True, blank=False)
    goles_visitante = models.IntegerField(null=True, blank=False)
    resultado_partido = models.CharField(max_length=1,choices=ResultadoPartido.choices,blank=False,null=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha = models.DateTimeField(null=True) #posiblemente se pueda usar null

    class Meta:
        verbose_name = "Partido" #le agrega ese nombre en la BD

    def __str__(self):
        return f'{self.equipo_local} vs {self.equipo_visitante}'

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
