# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt
# -*- coding: utf-8 -*-
from django.contrib.auth.models import Permission
from django.db.models import Q
from tls import request

from lizard_security.middleware import ALLOWED_DATA_SET_IDS
from lizard_security.middleware import USER_GROUP_IDS
from lizard_security.models import PermissionMapper


class LizardPermissionBackend(object):
    """Checker for object-level permissions via lizard-security."""

    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self):
        """Nope, we don't want to authenticate.

        Basic test:

          >>> lpb = LizardPermissionBackend()
          >>> lpb.authenticate()

        """
        pass

    def has_perm(self, user, perm, obj=None):
        """Return if we have a permission through a permission manager.

        Note: ``perm`` is a string like ``'testcontent.change_content'``, not
        a Permission object.

        We don't look at a user, just at user group membership. Our middleware
        translated logged in users to user group membership already.

        """
        if obj is None:
            # We' interested in a global permissions by definition. We only
            # deal with object-level permissions.
            return False
        try:
            user_group_ids = getattr(request, USER_GROUP_IDS, None)
            allowed_data_set_ids = getattr(request, ALLOWED_DATA_SET_IDS, None)
        except RuntimeError:
            # No tread-local request object.
            return False
        user_group_query = Q(user_group__id__in=user_group_ids)
        empty_data_set = Q(data_set=None)
        if allowed_data_set_ids:
            data_set_query = Q(data_set__in=allowed_data_set_ids) | empty_data_set
        else:
            data_set_query = empty_data_set
        relevant_permission_mappers = PermissionMapper.objects.filter(
            user_group_query & data_set_query)
        permissions = Permission.objects.filter(
            group__permissionmapper__in=relevant_permission_mappers)
        permissions = [(p.content_type.app_label + '.' + p.codename)
                       for p in permissions]
        return perm in permissions

    def has_module_perms(self, user_obj, app_label):
        """Return True if user_obj has any permissions in the given app_label.

        We only have to answer True for permissions that the user has through
        the permission mappers.

        This method is called by Django's admin

        """
        if app_label == 'lizard_security':
            # We need to grant access for user group managers.
            if user_obj.managed_user_groups.count():
                return True
        # TODO: grand permission to perms through perm managers.
        try:
            user_group_ids = getattr(request, USER_GROUP_IDS, None)
        except RuntimeError:
            # No tread-local request object.
            return False
        if user_group_ids:
            permissions = Permission.objects.filter(
                group__permissionmapper__user_group__id__in=user_group_ids)
            for perm in permissions:
                if perm.content_type.app_label == app_label:
                    return True
        return False
