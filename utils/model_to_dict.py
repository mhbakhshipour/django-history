from itertools import chain
from django.db.models.fields.related import ForeignKey, ManyToManyField


def model_to_dict(instance, fields=None, exclude=None, get_m2m_data_separated=False, get_data_with_str=False):
    opts = instance._meta
    concrete_fields = opts.concrete_fields
    private_fields = opts.private_fields
    many_to_many_fields = opts.many_to_many

    data = {}
    m2m_data = {}

    editable_fields = {f for f in chain(
        concrete_fields, private_fields, many_to_many_fields) if getattr(f, "editable", False)}

    for f in editable_fields:
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue

        field_value = f.value_from_object(instance)
        if isinstance(f, ForeignKey):
            if get_data_with_str:
                data[f.name] = getattr(instance, f.name).__str__()
            else:
                data[f.name + "_id"] = field_value
        elif isinstance(f, ManyToManyField):
            if get_data_with_str:
                data[f.name] = [i.__str__() for i in field_value]
                m2m_data[f.name] = [i.__str__() for i in field_value]
            else:
                data[f.name + "_ids"] = [i.id for i in field_value]
                m2m_data[f.name + "_ids"] = [i.id for i in field_value]
        else:
            data[f.name] = field_value

    if get_m2m_data_separated:
        return data, m2m_data
    return data
