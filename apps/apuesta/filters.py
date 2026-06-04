from django.db.models import Q
from django_filters import rest_framework as filters


class PartidoFilter(filters.FilterSet):
    estado = filters.CharFilter(field_name="estado",lookup_expr='icontains',label="Estado")

    equipo = filters.CharFilter(method="filtrar_equipo",lookup_expr='icontains',label='Equipo Buscado')

    def filtrar_equipo(self, queryset, name, value):
        return queryset.filter(
            Q(equipo_local__icontains=value) |
            Q(equipo_visitante__icontains=value)
        )