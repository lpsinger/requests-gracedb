def str_or_collection(values):
    if values is None:
        values = []
    elif isinstance(values, str):
        values = [values]
    return values


def field_collection(key, values):
    return [(key, value) for value in str_or_collection(values)]
