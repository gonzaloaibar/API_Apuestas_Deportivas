from rest_framework import serializers
from .models import Partido, Apuesta, TipoApuesta

class PartidoSerializer(serializers.ModelSerializer):

    #En el JSON de respuesta se mostrará el texto asigando a ResultadoPartido de models.py
    #lo cual es mas visual para el usuario final
    resultado_partido = serializers.CharField(
        source="get_resultado_partido_display",
        read_only=True
    )
    class Meta:
        model = Partido
        fields = '__all__'

class TipoApuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model=TipoApuesta
        fields='__all__'


class ApuestaSerializer(serializers.ModelSerializer):

    class Meta:
        model=Apuesta
        fields='__all__'
        read_only_fields = ['estado', 'cuota_aplicada', 'ganancia_casa', 'ganancia_cliente']

    # def create(self, validated_data):
    #     usuario = validated_data.pop('usuario', None)
    #     apuesta = Apuesta.objects.create(**validated_data)
    #
    #     return apuesta