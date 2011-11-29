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
import logging
import sys

from django.conf import settings

LIZARD_SECURITY_FILTERS = 'LIZARD_SECURITY_FILTERS'
DEFAULT_FILTERS = ['lizard_security.filters.data_set_filter']
_filter_functions = None
logger = logging.getLogger(__name__)


def filter_functions():
    """Return all filter functions from LIZARD_SECURITY_FILTERS."""
    global _filter_functions
    if _filter_functions is None:
        _filter_functions = []
        dotted_paths = getattr(settings,
                               LIZARD_SECURITY_FILTERS,
                               DEFAULT_FILTERS)
        for dotted_path in dotted_paths:
            if not '.' in dotted_path:
                logger.error(
                    "Filter function %r is not in dotted path notation.",
                    dotted_path)
                continue
            parts = dotted_path.rsplit('.')
            module_path = '.'.join(parts[:-1])
            function_name = parts[-1]
            __import__(module_path)
            module = sys.modules[module_path]
            function = getattr(module, function_name)
            _filter_functions.append(function)
            logger.debug("Added security filter %s from %s",
                         function_name, module_path)

    return _filter_functions


def security_filters(model_class):
    q_objects = []
    for filter_function in filter_functions():
        q_object = filter_function(model_class)
        if q_object is not None:
            q_objects.append(q_object)
    return q_objects
