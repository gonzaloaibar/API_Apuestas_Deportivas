from django.db import models

# Create your models here.
class Partido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('finalizado', 'Finalizado'),
    )
    RESULTADO = (
        ('gano_local','Ganó el equipo local'),
        ('gano_visitante','Ganó el equipo visitante'),
        ('empate','El partido termino en empate'),
    )
    api_football_id = models.IntegerField(unique=True)
    equipo_local = models.CharField(max_length=100)
    equipo_visitante = models.CharField(max_length=100)
    goles_local = models.IntegerField(null=True, blank=False)
    goles_visitante = models.IntegerField(null=True, blank=False)
    resultado_partido = models.CharField(max_length=30,choices=RESULTADO,blank=False,null=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha = models.DateTimeField(null=True) #posiblemente se pueda usar null

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
