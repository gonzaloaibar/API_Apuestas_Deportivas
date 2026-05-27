from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = '__all__'
        campos_extra = {
            "username": {"write_only":True},
            "password": {"write_only":True},
        }

    #Acá se va a hashear la contraseña del usuario
    def create(self, validated_data):
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)

        #metodo que hashea la contraseña
        usuario.set_password(password)

        usuario.save()

        return usuario