"""
Registry for filter functions
=============================

If a filter returns a `Q object
<https://docs.djangoproject.com/en/dev/topics/db/queries/#complex-lookups-with-q-objects>`_,
the Q object is added to EVERY object query that happens. So make sure you add
the right query!

A filter function should accept a Django model class and it should return
either None or a Q object.

"""

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
