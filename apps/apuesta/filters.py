from django_filters import rest_framework as filters


class PartidoFilter(filters.FilterSet):
    estado = filters.CharFilter(field_name="estado",lookup_expr='icontains')