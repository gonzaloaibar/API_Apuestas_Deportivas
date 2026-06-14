from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from .models import Partido, Apuesta, OpcionApuesta, Prediccion, TipoApuesta


#simplemente existe para ser usada por PartidoSerializer y mostrar esos dos atributos de la opcion de apuesta
class OpcionApuestaAuxiliarSerializer(serializers.ModelSerializer):
    prediccion = serializers.CharField(
        source='get_prediccion_display',
        read_only = True
    )

    class Meta:
        model = OpcionApuesta
        fields = [
            "uuid",
            "prediccion",
            "multiplicador"
        ]


class OpcionApuestaSerializer(serializers.ModelSerializer):

    descripcion = serializers.SerializerMethodField()
    partido_id = serializers.SerializerMethodField()

    partido = serializers.SlugRelatedField(
        queryset=Partido.objects.all(),
        slug_field="uuid"
    )

    class Meta:
        model=OpcionApuesta
        fields = [
            "uuid",
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

        partido=attrs.get("partido")
        tipo_apuesta=attrs.get("tipo_apuesta")
        prediccion=attrs.get("prediccion")

        # Si estamos en PATCH y no vino el campo, tomamos el valor actual
        if self.instance:
            partido = partido or self.instance.partido
            tipo_apuesta = tipo_apuesta or self.instance.tipo_apuesta
            prediccion = prediccion or self.instance.prediccion

        # controlo que el partido no esté finalizado
        if partido and partido.estado == "finalizado":
            raise serializers.ValidationError(
                "No puede crear una opción de apuesta en un partido finalizado."
            )

        #el tipo de apuesta y la prediccion deben coincidir
        predicciones_resultado = {
            Prediccion.GANA_LOCAL,
            Prediccion.EMPATE,
            Prediccion.GANA_VISITANTE,
        }

        predicciones_goles = {
            Prediccion.MAS_1_GOL,
            Prediccion.MAS_3_GOLES,
            Prediccion.MAS_5_GOLES,
        }

        if (
                tipo_apuesta == TipoApuesta.RESULTADO
                and prediccion not in predicciones_resultado
        ):
            raise serializers.ValidationError(
                {"prediccion":"La predicción no corresponde a una apuesta de resultado."}
            )

        if (
                tipo_apuesta == TipoApuesta.GOLES
                and prediccion not in predicciones_goles
        ):
            raise serializers.ValidationError(
                {"prediccion":"La predicción no corresponde a una apuesta de cantidad de goles."}
            )

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

    def update(self, instance, validated_data):

        instance.multiplicador = validated_data.get("multiplicador",instance.multiplicador)
        instance.monto_minimo = validated_data.get("monto_minimo",instance.monto_minimo)

        instance.prediccion = validated_data.get("monto_minimo", instance.prediccion)

        instance.save()
        return instance



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
            "uuid",
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

    # opcion_apuesta = serializers.PrimaryKeyRelatedField(
    #     queryset=OpcionApuesta.objects.all(),
    #     write_only=True
    # )
    opcion_apuesta = serializers.SlugRelatedField(
        queryset=OpcionApuesta.objects.all(),
        slug_field="uuid"
    )
    prediccion=serializers.SerializerMethodField()

    partido=serializers.SerializerMethodField()

    class Meta:
        model=Apuesta
        fields=[
            "uuid",
            "opcion_apuesta",
            "monto_apostado",
            "estado",
            "ganancia_cliente",
            "fecha",
            "apostado_por",
            "partido",
            "prediccion"
        ]
        #fields = "__all__"
        read_only_fields = ["uuid", 'ganancia_cliente', 'ganancia_casa', 'estado', 'apostado_por']


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


    #validacion para el monto apostado, y para que no se repita la misma opcion de apuesta dos veces en el mismo partido y por el mismo usuario
    def validate(self, attrs):

        opcion = attrs.get("opcion_apuesta")
        monto = attrs.get("monto_apostado")

        #pregunto si en la request existe opcion y monto, si no existen significa que estoy haciendo un patch
        if self.instance:

            if opcion is None:
               opcion = self.instance.opcion_apuesta #traigo la opcion de la instancia que estoy modificando

            if monto is None:
               monto = self.instance.monto_apostado #traigo el monto de la instancia que estoy modificando

        #pregunto si el monto apostado es mayor al minimo
        if monto < opcion.monto_minimo:
            raise serializers.ValidationError(
                f"El monto mínimo es {opcion.monto_minimo}"
            )

        # context->cabezera con la informacion del usuario
        usuario = self.context['request'].user

        #consulto si existe ya una apuesta de este usuario para este partido con esta misma predicción
        queryset = Apuesta.objects.filter(apostado_por=usuario, opcion_apuesta__partido=opcion.partido,
                                        opcion_apuesta__prediccion=opcion.prediccion)

        # Si estoy editando una apuesta, excluyo la actual, esto para que nme permita el patch
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Ya realizo una apuesta con esa prediccion para este partido")

        return attrs

