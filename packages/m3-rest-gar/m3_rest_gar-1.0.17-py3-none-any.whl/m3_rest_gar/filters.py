import operator
from functools import (
    reduce,
)

from django.db.models import (
    Q,
)
from django_filters.rest_framework import (
    BaseInFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
)

from m3_gar.models import (
    AddrObj,
    Apartments,
    Houses,
    Rooms,
)
from m3_rest_gar.util import (
    filter_by_parentobjid,
)


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CharInFilter(BaseInFilter, CharFilter):
    pass


class HierarchyParentFilter(CharFilter):
    """
    Фильтр по objectid родителя в иерархии адресных объектов.
    На вход фильтра ожидается строка вида `hierarchy:parentobjid`
    Более подробно см. `m3_rest_gar.util.filter_by_parentobjid`
    """

    def filter(self, qs, value):
        if value:
            try:
                hierarchy, objectid = value.split(':')
            except ValueError:
                pass
            else:
                qs = filter_by_parentobjid(hierarchy, qs, objectid)

        return qs


class AddrObjFilter(FilterSet):
    """
    Фильтр сведений классификатора адресообразующих элементов
    """
    level = NumberInFilter(field_name='level')
    parent = HierarchyParentFilter()
    name = CharFilter(lookup_expr='icontains')
    name__exact = CharFilter(lookup_expr='exact')
    typename = CharInFilter(field_name='typename')

    class Meta:
        model = AddrObj
        fields = ['level', 'parent', 'name', 'name__exact', 'typename']


class HousesFilter(FilterSet):
    """
    Фильтр сведений по номерам домов улиц городов и населенных пунктов
    """
    parent = HierarchyParentFilter()
    housenum = CharFilter(method='_housenum', lookup_expr='icontains')
    housenum__exact = CharFilter(method='_housenum', lookup_expr='exact')

    class Meta:
        model = Houses
        fields = ['parent', 'housenum', 'housenum__exact']

    def _housenum(self, qs, name, value):
        """
        Фильтр по номеру дома также должен учитывать дополнительные номера дома
        """
        filter_field = self.filters[name]
        lookup_expr = filter_field.lookup_expr

        fields = ['housenum', 'addnum1', 'addnum2']
        filters = [
            Q(**{
                f'{field}__{lookup_expr}': value,
            }) for field in fields
        ]
        q = reduce(operator.or_, filters, Q())
        qs = qs.filter(q)

        return qs


class ApartmentsFilter(FilterSet):
    """
    Фильтр сведений по помещениям
    """
    parent = HierarchyParentFilter()
    number = CharFilter(lookup_expr='icontains')
    number__exact = CharFilter(lookup_expr='exact')

    class Meta:
        model = Apartments
        fields = ['parent', 'number', 'number__exact']


class RoomsFilter(FilterSet):
    """
    Фильтр сведений по комнатам
    """
    parent = HierarchyParentFilter()
    number = CharFilter(lookup_expr='icontains')
    number__exact = CharFilter(lookup_expr='exact')

    class Meta:
        model = Rooms
        fields = ['parent', 'number', 'number__exact']
