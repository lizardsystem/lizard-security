from django.db.models import Q
from tls import request


def data_set_filter(model_class):
    """Filter that checks if we're properly allowed via the dataset.

    We only operate on models that have a direct link to a data set.

    If data set is empty, that counts as "everybody has access". Otherwise we
    only have access to data sets available to us as user.

    """
    if not hasattr(model_class, 'data_set'):
        return
    empty_data_set = Q(data_set=None)
    try:
        user = request.user
    except RuntimeError:
        # We don't have a local request object.
        return empty_data_set
    if user is not None and user.is_superuser:
        return
    try:
        data_set_ids = request.data_set_ids
    except AttributeError:
        return empty_data_set
    match_with_data_set = Q(data_set__in=data_set_ids)
    return empty_data_set | match_with_data_set

