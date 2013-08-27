# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt
# -*- coding: utf-8 -*-
"""
To securely filter our objects we don't have access to, we use a custom Django
object manager: ``FilteredManager``. We have to set that object manager on our
models.

"""
from django.contrib.gis.db.models import GeoManager
from django.db.models.manager import Manager
from django.db.models import Q
from tls import request

from lizard_security.middleware import ALLOWED_DATA_SET_IDS


def data_set_filter(model_class):
    """Filter that checks if we're properly allowed via the dataset.

    If data set is empty, that counts as "everybody has access". Otherwise we
    only have access to data sets available to us as user.

    """
    empty_data_set = Q(data_set=None)
    try:
        user = request.user
    except RuntimeError:
        # We don't have a local request object.
        return
    if user is not None and user.is_superuser:
        return
    data_set_ids = getattr(request, ALLOWED_DATA_SET_IDS, None)
    if data_set_ids:
        match_with_data_set = Q(data_set__in=data_set_ids)
        return empty_data_set | match_with_data_set
    else:
        return empty_data_set


class FilteredManagerMixin(object):
    """Custom manager that filters out objects whose data set we can't access.
    """

    # Note: Django's docs discourage setting this to True for managers
    # that filter away rows from a query set and are used as a model's
    # default manager (as this one is intended to be), because Django internally
    # sometimes relies on getting everything back.

    # However, we think it is still OK here, because we only filter away things
    # if a request object is available. Outside of a request/response context,
    # nothing is filtered.

    # Finally, setting it here implies that it is also True for GeoManager, and
    # we don't know if that does something dangerous. Luckily that is of no
    # concern since GeoManager itself also sets use_for_related_fields to True.

    # What this _does_ is that models that have a normal manager, that
    # have foreign keys to models controlled by lizard-security will
    # get ObjectDoesNotExist in case the foreign key leads to an
    # object from a dataset to which the current user does not have
    # access.
    use_for_related_fields = True

    def get_query_set(self):
        """Return base queryset, filtered through lizard-security's mechanism.
        """
        query_set = super(FilteredManagerMixin, self).get_query_set()
        extra_filter = data_set_filter(self.model)
        if extra_filter is not None:
            query_set = query_set.filter(extra_filter)
        return query_set


class FilteredManager(FilteredManagerMixin, Manager):
    pass


class FilteredGeoManager(FilteredManagerMixin, GeoManager):
    pass
