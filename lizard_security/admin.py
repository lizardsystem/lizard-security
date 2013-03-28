# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt
# -*- coding: utf-8 -*-
"""
Lizard-security's ``admin.py`` contains two kinds of model admins:

- Our own model admins to make editing data sets, permission mappers and user
  groups easier.

- ``SecurityFilteredAdmin`` as a base class for admins of models that use
  lizard-security's data set mechanism.

"""
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.forms import ModelForm
from tls import request as tls_request

from lizard_security.middleware import USER_GROUP_IDS
from lizard_security.models import DataOwner
from lizard_security.models import DataSet
from lizard_security.models import PermissionMapper
from lizard_security.models import UserGroup


class DataOwnerAdmin(admin.ModelAdmin):
    """Docstring."""
    filter_horizontal = ('data_managers', )


class DataSetAdmin(admin.ModelAdmin):
    """Unmodified admin for data sets."""
    model = DataSet
    list_display = ('name', 'owner', )


class UserGroupAdminForm(ModelForm):
    """Custom form for user groups: ensures managers are also members.

    A user group's manager should also automatically be a member. Otherwise
    we'd need two queries to determine user group membership, now only one.

    """
    class Meta:
        model = UserGroup

    def clean(self):
        """Make sure all managers are also members."""
        members = list(self.cleaned_data['members'])
        for manager in self.cleaned_data['managers']:
            if manager not in members:
                members.append(manager)
        self.cleaned_data['members'] = members
        return self.cleaned_data


class UserGroupAdmin(admin.ModelAdmin):
    """Custom admin for user groups: show manager/membership info directly.

    User groups are also filtered to only those you are a manager of.

    """
    model = UserGroup
    form = UserGroupAdminForm
    list_display = ('name', 'manager_info', 'number_of_members')
    search_fields = ('name', )
    filter_horizontal = ('managers', 'members')

    def queryset(self, request):
        """Limit user groups to those you manage.

        The superuser can edit all user groups, of course.

        """
        qs = super(UserGroupAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id__in=request.user.managed_user_groups.all())


class PermissionMapperAdmin(admin.ModelAdmin):
    """Custom admin for permission mapper: editable in the list display.

    The most important items, data set and permission group, are editable in
    the list display. The list display also gives you a good view on all data,
    which is needed to keep track of all the various security settings if you
    have more than a handful of permission mappers.

    """
    model = PermissionMapper
    list_display = ('name', 'user_group', 'data_set', 'permission_group')
    list_editable = ('user_group', 'data_set', 'permission_group')
    list_filter = ('user_group', 'data_set', 'permission_group')
    search_fields = ('name', 'data_set__name')


class SecurityFilteredAdmin(admin.ModelAdmin):
    """Custom admin base class for models that use lizard-security data sets.

    Django's default admin looks at global permissions to determine if you can
    even view a certain model in the admin. SecurityFilteredAdmin takes
    lizard-security's permission mapper into account.

    """

    def _available_permissions(self):
        """Return all permissions we have through user group membership.

        This method is used by the ``has_{add|change|delete}_permission()``
        methods. They have to determine whether we have rights to
        add/change/delete *some* instance of the model we're the admin for. So
        we don't have to look at data sets, only at which permissions are
        somehow connected to the user groups we're a member of.

        """
        user_group_ids = getattr(tls_request, USER_GROUP_IDS, None)
        if user_group_ids:
            permissions = Permission.objects.filter(
                group__permissionmapper__user_group__id__in=user_group_ids)
            permissions = [(perm.content_type.app_label + '.' + perm.codename)
                           for perm in permissions]
            return permissions
        return []

    def has_add_permission(self, request):
        """Return True if the given request has permission to add an object.
        """
        opts = self.opts
        perm = opts.app_label + '.' + opts.get_add_permission()
        if request.user.has_perm(perm):
            return True
        return perm in self._available_permissions()

    def has_change_permission(self, request, obj=None):
        """Return True if we have permission to change the object.

        If ``obj`` is None, we just have to check if we have global
        permissions or if we have the permission through a permission mapper.

        TODO: specific check for object permissions.

        """
        opts = self.opts
        perm = opts.app_label + '.' + opts.get_change_permission()
        # TODO: object permissions
        if request.user.has_perm(perm):
            return True
        result = perm in self._available_permissions()
        print "%r in %s: %s" % (perm, self._available_permissions(), result)
        return result

    def has_delete_permission(self, request, obj=None):
        """Return True if we have permission to delete the object.

        If ``obj`` is None, we just have to check if we have global
        permissions or if we have the permission through a permission mapper.

        TODO: specific check for object permissions.

        """
        opts = self.opts
        perm = opts.app_label + '.' + opts.get_delete_permission()
        # TODO: object permissions
        if request.user.has_perm(perm):
            return True
        return perm in self._available_permissions()


admin.site.register(DataOwner, DataOwnerAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(PermissionMapper, PermissionMapperAdmin)
