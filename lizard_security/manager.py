# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt
# -*- coding: utf-8 -*-
"""
To securely filter objects we don't have access to, we use a custom Django
object manager: ``TimeseriesManager``. We have to set that object manager
on our models.

"""
from django.contrib.gis.db.models import GeoManager
from django.contrib.gis.db.models.query import GeoQuerySet
from django.db.models.manager import Manager
from django.db.models import Q
from tls import request
from treebeard.mp_tree import MP_NodeManager
from treebeard.mp_tree import MP_NodeQuerySet


class FilteredManager(Manager):
    # For backwards compatibility with lizard-ui.
    pass


def filter_by_permissions(query_set, relation):
    if not request:
        # Not running in site-context, so no extra filtering.
        return query_set
    user = getattr(request, 'user', None)
    if user and user.is_superuser:
        # User is admin, so no extra filtering.
        return query_set
    args = []
    relation = relation + ["permission_mappers", "user_group", "id", "in"]
    kwargs = {"__".join(relation): getattr(request, 'user_group_ids', [])}
    return query_set.filter(*args, **kwargs).distinct()


class TimeseriesManager(Manager):
    """Manager that filters out ``Timeseries`` we have no permissions for."""

    def get_query_set(self):
        """Return base queryset, filtered by lizard-security's mechanism."""
        query_set = super(TimeseriesManager, self).get_query_set()
        return filter_by_permissions(query_set, ["data_set"])


class DataSetManager(Manager):
    """Manager that filters out ``Timeseries`` we have no permissions for."""

    def get_query_set(self):
        """Return base queryset, filtered by lizard-security's mechanism."""
        query_set = super(DataSetManager, self).get_query_set()
        return filter_by_permissions(query_set, [])


class LocationQuerySet(GeoQuerySet, MP_NodeQuerySet):
    """Custom QuerySet that combines ``GeoQuerySet`` and ``MP_NodeQuerySet``.

    This tackles multiple inheritance problems: see ``LocationManager``.
    Note that while both super classes currently do have distinct
    methods, this might not be the case in the future.

    """

    def __init__(self, *args, **kwargs):
        super(LocationQuerySet, self).__init__(*args, **kwargs)


class LocationManager(GeoManager, MP_NodeManager):
    """Custom manager for the ``Location`` model class.

    We are bitten by multiple inheritance here: a ``GeoManager`` is required to
    support spatial queries, while an ``MP_NodeManager`` is needed by django-
    treebeard for manipulating trees. Both managers override get_query_set!
    This is solved by creating a custom ``LocationQuerySet``.

    """

    def get_query_set(self):
        # Satisfy both GeoManager and MP_NodeManager:
        query_set = LocationQuerySet(self.model,
            using=self._db).order_by('path')
        return filter_by_permissions(query_set, ["timeseries", "data_set"])


class LogicalGroupManager(Manager):
    """Manager that filters out ``Timeseries`` we have no permissions for."""

    def get_query_set(self):
        """Return base queryset, filtered by lizard-security's mechanism."""
        query_set = super(LogicalGroupManager, self).get_query_set()
        return filter_by_permissions(query_set, ["timeseries", "data_set"])
