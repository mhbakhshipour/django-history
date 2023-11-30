from typing import Any

from itertools import chain
from django.db.models.fields.related import ForeignKey, ManyToManyField


def model_to_dict(
    instance: Any,
    fields: list = None,
    exclude: list = None,
    get_m2m_data_separated: bool = False,
    get_data_with_str: bool = False,
    depth: int = 0,
) -> tuple[dict, dict] | dict:
    opts = instance._meta
    concrete_fields = opts.concrete_fields
    private_fields = opts.private_fields
    many_to_many_fields = opts.many_to_many

    data = {}
    m2m_data = {}

    editable_fields = {
        f
        for f in chain(concrete_fields, private_fields, many_to_many_fields)
        if getattr(f, "editable", False)
    }

    for f in editable_fields:
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue

        field_value = f.value_from_object(instance)

        if isinstance(f, ForeignKey):
            if get_data_with_str:
                data[f.name] = str(getattr(instance, f.name))
            else:
                data[f.name + "_id"] = field_value
                if depth > 0:
                    data[f.name] = model_to_dict(
                        getattr(instance, f.name), depth=depth - 1
                    )

        elif isinstance(f, ManyToManyField):
            if get_data_with_str:
                data[f.name] = [str(i) for i in field_value]
                m2m_data[f.name] = [str(i) for i in field_value]
            else:
                data[f.name + "_ids"] = [i.id for i in field_value]
                m2m_data[f.name + "_ids"] = [i.id for i in field_value]
                if depth > 0:
                    data[f.name] = [
                        model_to_dict(i, depth=depth - 1) for i in field_value
                    ]
        else:
            data[f.name] = field_value

    if get_m2m_data_separated:
        return data, m2m_data
    return data
