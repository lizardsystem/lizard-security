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


def is_admin():
    if request:
        user = getattr(request, 'user', None)
        return user and user.is_superuser
    return True


class TimeseriesManager(Manager):
    """Manager that filters out ``Timeseries`` we have no permissions for."""

    def get_query_set(self):
        """Return base queryset, filtered by lizard-security's mechanism."""
        query_set = super(TimeseriesManager, self).get_query_set()
        if is_admin():
            return query_set
        return query_set.filter(
            data_set__permission_mappers__user_group__id__in=
            getattr(request, 'user_group_ids', [])).distinct()


class DataSetManager(Manager):
    """Manager that filters out ``Timeseries`` we have no permissions for."""

    def get_query_set(self):
        """Return base queryset, filtered by lizard-security's mechanism."""
        query_set = super(DataSetManager, self).get_query_set()
        if is_admin():
            return query_set
        return query_set.filter(
            permission_mappers__user_group__id__in=
            getattr(request, 'user_group_ids', [])).distinct()


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
        if is_admin():
            return query_set
        return query_set.filter(
            timeseries__data_set__permission_mappers__user_group__id__in=
            getattr(request, 'user_group_ids', [])).distinct()


class LogicalGroupManager(Manager):
    """Manager that filters out ``Timeseries`` we have no permissions for."""

    def get_query_set(self):
        """Return base queryset, filtered by lizard-security's mechanism."""
        query_set = super(LogicalGroupManager, self).get_query_set()
        if is_admin():
            return query_set
        return query_set.filter(
            timeseries__data_set__permission_mappers__user_group__id__in=
            getattr(request, 'user_group_ids', [])).distinct()
