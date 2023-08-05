from collections.abc import (
    Iterable,
)
from uuid import (
    UUID,
)

from django.db.models import (
    Q,
)

from m3_gar.models.hierarchy import (
    Hierarchy,
)


# Пример административного деления
# 33634065 - д 54
# 210826 - ул Заречная
# 210984 - с Кунгуртуг
# 213492 - р-н Тере-Хольский
# 206101 - Респ Тыва

# Пример муниципального деления
# 33634065 - д 54
# 210826 - ул Заречная
# 210984 - с Кунгуртуг
# 95235279 - с.п. Шынаанский
# 95235278 - м.р-н Тере-Хольский
# 206101 - Респ Тыва

def filter_by_parentobjid(hierarchy, qs, parentobjid):
    """
    Фильтрация queryset адресных объектов по их родителю

    Args:
        hierarchy: Код или список кодов иерархии, по которым будет проводиться
            фильтрация. Объекты фильтруются по совпадению родителя хотя бы в
            одной иерархии. Коды иерархии могут принимать значения `adm`, `mun`.
            Для поиска по всем известным иерархиям используется значение `any`.
        qs: QuerySet адресных объектов (AddrObj, Houses, Apartments, Rooms,
            Carplaces, Steads), либо объектов реестра (ReestrObjects)
        parentobjid: objectid родительского адресного объекта

    Returns:
        Отфильтрованный queryset адресных объектов

    """
    hierarchy_model_map = Hierarchy.get_shortname_map()

    if hierarchy == 'any':
        hierarchy = hierarchy_model_map.keys()
    elif isinstance(hierarchy, str):
        hierarchy = [hierarchy]
    elif isinstance(hierarchy, Iterable):
        pass
    else:
        raise TypeError(f'Invalid hierarchy value: {hierarchy}')

    if is_objectguid(parentobjid):
        filter_key = 'parentobjid__objectguid'
    else:
        filter_key = 'parentobjid__objectid'

    objectid_filter = Q()

    for h in hierarchy:
        if h not in hierarchy_model_map:
            raise ValueError(f'Invalid hierarchy value: {h}')

        hierarchy_model = hierarchy_model_map[h]

        objectid_filter |= Q(
            objectid__in=hierarchy_model.objects.filter(**{
                'isactive': True,
                filter_key: parentobjid,
            }).values('objectid'),
        )

    return qs.filter(objectid_filter)


def is_objectguid(value):
    try:
        UUID(value)
    except ValueError:
        result = False
    else:
        result = True

    return result
