

_filter_functions = []


def register(function):
    _filter_functions.append(function)


def security_filters(model_class):
    q_objects = []
    for filter_function in _filter_functions:
        q_object = filter_function(model_class)
        if q_object is not None:
            q_objects.append(q_object)
    return q_objects
