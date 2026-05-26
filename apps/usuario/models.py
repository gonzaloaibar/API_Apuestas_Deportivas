from django.db import models
from django.contrib.auth.models import AbstractUser
from numpy.ma.core import negative


# Create your models here.

class Usuario(AbstractUser):
    nombre = models.CharField(max_length=50,null=False,blank=False)
    cuil = models.CharField(max_length=11,verbose_name="cuil",unique=True)
    numero_de_cuenta = models.CharField(max_length=30,null=False,blank=False)
    saldo = models.DecimalField(default=0,null=False,blank=False)

    def __str__(self):
        return f'Usuario:  {self.nombre}'

