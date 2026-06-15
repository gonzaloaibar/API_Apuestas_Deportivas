from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from .models import Partido, Apuesta, OpcionApuesta, Prediccion, TipoApuesta
from .. import apuesta


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

    # partido = serializers.PrimaryKeyRelatedField(
    #     queryset=Partido.objects.all(),
    #     write_only=True
    # )
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

        partido=attrs["partido"]
        tipo_apuesta=attrs["tipo_apuesta"]
        prediccion=attrs["prediccion"]

        #no se puede crear una opcion de apuesta para un partido finalizado
        if partido.estado=="finalizado":
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
                "La predicción no corresponde a una apuesta de resultado."
            )

        if (
                tipo_apuesta == TipoApuesta.GOLES
                and prediccion not in predicciones_goles
        ):
            raise serializers.ValidationError(
                "La predicción no corresponde a una apuesta de cantidad de goles."
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

class ApuestaValidator:

    @staticmethod
    def validar_apuesta_pendiente(apuesta):

        if apuesta.estado != "pendiente":
            raise serializers.ValidationError(
                "Solo se pueden modificar apuestas pendientes."
            )

    @staticmethod
    def validate_opcion_apuesta(opcion):
        if opcion.partido.estado != "pendiente":
            raise serializers.ValidationError(
                "No se puede apostar sobre un partido finalizado."
            )

    @staticmethod
    def validar_monto_minimo(opcion,monto):
        if monto < opcion.monto_minimo:
            raise serializers.ValidationError(
                f"El monto mínimo es {opcion.monto_minimo}"
            )

    @staticmethod
    def validar_prediccion_duplicada(usuario,opcion,apuesta_actual=None):

        queryset = Apuesta.objects.filter(
            apostado_por=usuario,
            opcion_apuesta__partido=opcion.partido,
            opcion_apuesta__prediccion=opcion.prediccion
        )

        # Si estoy modificando una apuesta,
        # excluyo la apuesta actual.
        if apuesta_actual:
            queryset = queryset.exclude(
                pk=apuesta_actual.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya realizó una apuesta con esa predicción para este partido."
            )

#serializador extra para la modificacion de apuesta
class ModificarApuestaSerializer(serializers.Serializer):

    opcion_apuesta = serializers.SlugRelatedField(
        queryset=OpcionApuesta.objects.all(),
        slug_field="uuid",
        required=False
    )

    monto_apostado = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        required=False
    )

    #validaciones
    def validate(self, attrs):
        apuesta = self.instance

        opcion = attrs.get("opcion_apuesta",apuesta.opcion_apuesta)

        monto = attrs.get("monto_apostado",apuesta.monto_apostado)

        usuario = self.context["request"].user

        ApuestaValidator.validar_apuesta_pendiente(apuesta)

        ApuestaValidator.validate_opcion_apuesta(opcion)

        ApuestaValidator.validar_monto_minimo(opcion,monto)

        ApuestaValidator.validar_prediccion_duplicada(usuario,opcion,apuesta_actual=apuesta)

        return attrs


class ApuestaSerializer(serializers.ModelSerializer):

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

    #validaciones

    def validate(self, attrs):
        opcion = attrs["opcion_apuesta"]
        monto = attrs["monto_apostado"]

        usuario = self.context["request"].user

        ApuestaValidator.validate_opcion_apuesta(opcion)

        ApuestaValidator.validar_monto_minimo(opcion,monto)

        ApuestaValidator.validar_prediccion_duplicada(usuario,opcion)

        return attrs
