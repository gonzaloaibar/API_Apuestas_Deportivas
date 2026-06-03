from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class Usuario(AbstractUser):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    nombre = models.CharField(max_length=50,null=False,blank=False)
    apellido = models.CharField(max_length=50,null=False,blank=False)
    cuil = models.CharField(max_length=11,verbose_name="cuil",unique=True)
    numero_de_cuenta = models.CharField(max_length=15,blank=True,unique=True)
    saldo = models.DecimalField(default=0,null=False,blank=False,decimal_places=2,max_digits=20)

    def __str__(self):
        return f'Usuario:  {self.nombre}'

    #logica para asignar un numero de cuenta, la logica puede cambiar
    #pero en esta estapa será el prefijo CTA + - + cuil = 15 caracteres
    def asignar_numero_de_cuenta(self):

        return f'CAT-{self.cuil}'

    #antes de guardar se asigna el numero de cuenta
    def save(self,*args,**kwargs):
        #como no tendra numero de cuenta ingresara al if
        if not self.numero_de_cuenta:
            self.numero_de_cuenta = self.asignar_numero_de_cuenta()

        super().save(*args,**kwargs)