from django.db import models
from apps.usuario.models import Usuario

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

class TipoApuesta(models.TextChoices):
    RESULTADO = "resultado", "Resultado"
    GOLES = "cantidad_goles", "Cantidad de goles"

class Prediccion(models.TextChoices):
    GANA_LOCAL = "gana_local", "Gana Local"
    EMPATE = "empate", "Empate"
    GANA_VISITANTE = "gana_visitante", "Gana Visitante"

    MAS_1_GOL = "mas_1_gol", "Más de 1 gol"
    MAS_3_GOLES = "mas_3_goles", "Más de 3 goles"
    MAS_5_GOLES = "mas_5_goles", "Más de 5 goles"

class OpcionApuesta(models.Model):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    tipo_apuesta = models.CharField(max_length=100, choices=TipoApuesta.choices,blank=False,null=False)
    prediccion = models.CharField(max_length=100, choices=Prediccion.choices,blank=True,null=True)
    multiplicador=models.DecimalField(max_digits=3, decimal_places=2, null=False)
    monto_minimo=models.DecimalField(max_digits=20, decimal_places=2, null=False, default=0)


class Apuesta(models.Model):
    ESTADOS = (
        ("pendiente", "Pendiente"),
        ("ganada", "Ganada"),
        ("perdida", "Perdida"),
    )

    apostado_por=models.ForeignKey("usuario.Usuario",on_delete=models.CASCADE,  related_name='apuestas')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    opcion_apuesta = models.ForeignKey(OpcionApuesta, on_delete=models.CASCADE)
    monto_apostado= models.DecimalField(max_digits=10, decimal_places=2)
    #cuota_aplicada = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(default="pendiente", max_length=100, choices=ESTADOS)
    ganancia_cliente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ganancia_casa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.opcion_apuesta.nombre},{self.partido},{self.estado},{self.ganancia_casa},{self.fecha}'

