from rest_framework import serializers
from .models import Partido, Apuesta

class PartidoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Partido
        fields = '__all__'

class ApuestaSerializer(serializers.ModelSerializer):

    class Meta:
        model=Apuesta
        fields='__all__'