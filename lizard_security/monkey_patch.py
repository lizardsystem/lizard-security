"""Monkey patch for always filtering Django models.

This file is imported in our ``models.py``, which is early enough.

"""
from django.db.models.query import QuerySet
from django.db.models.manager import Manager

from lizard_security import filter_registry


def patched_get_query_set(self):
    query_set = QuerySet(self.model, using=self._db)
    for security_filter in filter_registry.security_filters(self.model):
        # A security filter is a "Q" object.
        query_set = query_set.filter(security_filter)
    return query_set


Manager.get_query_set = patched_get_query_set
print("Patched Django's default object manager")
