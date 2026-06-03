from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario

        fields = [
            "uuid",
            "username",
            "password",
            "nombre",
            "apellido",
            "cuil",
            "numero_de_cuenta",
            "saldo"
        ]

        extra_kwargs = {
            "password": {
                "write_only": True #el serializer no devolvera la contraseña
            }
        }

    #Acá se va a hashear la contraseña del usuario
    def create(self, validated_data):

        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)

        #metodo que hashea la contraseña
        usuario.set_password(password)

        usuario.save()

        return usuario