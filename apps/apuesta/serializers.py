from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from .models import Partido, Apuesta, OpcionApuesta

#simplemente existe para ser usada por PartidoSerializer y mostrar esos dos atributos de la opcion de apuesta
class OpcionApuestaAuxiliarSerializer(serializers.ModelSerializer):
    prediccion = serializers.CharField(
        source='get_prediccion_display',
        read_only = True
    )

    class Meta:
        model = OpcionApuesta
        fields = [
            "prediccion",
            "multiplicador"
        ]


class OpcionApuestaSerializer(serializers.ModelSerializer):

    descripcion = serializers.SerializerMethodField()
    partido_id = serializers.SerializerMethodField()

    class Meta:
        model=OpcionApuesta
        fields = [
            "id",
            "tipo_apuesta",
            "prediccion",
            "partido",
            "multiplicador",
            "monto_minimo",
            "partido_id",
            "descripcion"
        ]

    def get_partido_id(self, obj):
        return(
            f"{obj.partido.id}"
        )

    def get_descripcion(self, obj):
        return (
            f"{obj.partido.equipo_local} vs "
            f"{obj.partido.equipo_visitante} - "
            f"{obj.get_prediccion_display()}"
        )

    def validate (self, attrs):

        partido=attrs["partido"]
        tipo_apuesta=attrs["tipo_apuesta"]
        prediccion=attrs["prediccion"]

        queryset=OpcionApuesta.objects.filter(partido=partido, tipo_apuesta=tipo_apuesta, prediccion=prediccion)

        #ya existe la instancia y solo la quiero modificar
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        #quiero crear una opcion que ya existe en la db
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una opcion de apuesta con esa prediccion para ese partido"
            )
        return attrs


class PartidoSerializer(serializers.ModelSerializer):

    #En el JSON de respuesta se mostrará el texto asigando a ResultadoPartido de models.py
    #lo cual es mas visual para el usuario final
    resultado_partido = serializers.CharField(
        source="get_resultado_partido_display",
        read_only=True
    )

    opciones_apuesta = OpcionApuestaAuxiliarSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Partido
        fields = [
            "id",
            "equipo_local",
            "equipo_visitante",
            "estado",
            "fecha",
            "opciones_apuesta",
            "resultado_partido",
            "goles_local",
            "goles_visitante",
        ]

    #uso to_representation para que esos campos devuelvan null si la apuesta sigue pendiente
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.estado == "pendiente":
            data["resultado_partido"] = None
            data["goles_local"] = None
            data["goles_visitante"] = None

        return data


class ApuestaSerializer(serializers.ModelSerializer):

    opcion_apuesta = serializers.PrimaryKeyRelatedField(
        queryset=OpcionApuesta.objects.all(),
        write_only=True
    )

    prediccion=serializers.SerializerMethodField()

    partido=serializers.SerializerMethodField()

    class Meta:
        model=Apuesta
        fields=[
            "id",
            "opcion_apuesta",
            "monto_apostado",
            "estado",
            "ganancia_cliente",
            "ganancia_casa",
            "fecha",
            "apostado_por",
            "partido",
            "prediccion"
        ]
        read_only_fields = ['id', 'ganancia_cliente', 'ganancia_casa', 'estado', 'apostado_por']


    def get_prediccion(self, obj):
        return(
            f"{obj.opcion_apuesta.get_prediccion_display()} - "
            f"{obj.opcion_apuesta.multiplicador}"
        )

    def get_partido(self, obj):
        return(
            f"{obj.opcion_apuesta.partido.equipo_local} vs "
            f"{obj.opcion_apuesta.partido.equipo_visitante} - "
            f"ID = {obj.opcion_apuesta.partido.id}"
        )

    #validacion para que solo se pueda apostar sobre un partido pendiente
    def validate_opcion_apuesta(self, opcion):
        if opcion.partido.estado != "pendiente":
            raise serializers.ValidationError(
                "No se puede apostar sobre un partido finalizado."
            )

        return opcion

    #validacion para que el monto apostado sea mayor al monto minimo
    def validate(self, attrs):

        opcion = attrs["opcion_apuesta"]
        monto = attrs["monto_apostado"]

        if monto < opcion.monto_minimo:
            raise serializers.ValidationError(
                f"El monto mínimo es {opcion.monto_minimo}"
            )

        return attrs