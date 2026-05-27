from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = [
        "id",
        "username",
        "nombre",
        "apellido",
        ]
        read_only_fields = ["cuil","numero_de_cuenta","saldo",]

    #Acá se va a hashear la contraseña del usuario
    def create(self, validated_data):
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)

        #metodo que hashea la contraseña
        usuario.set_password(password)

        usuario.save()

        return usuario