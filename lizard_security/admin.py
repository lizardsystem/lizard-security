from django.contrib import admin
from django.contrib.auth.models import Permission
from tls import request as tls_request
from django.forms import ModelForm

from lizard_security.models import DataSet
from lizard_security.models import PermissionMapper
from lizard_security.models import UserGroup
from lizard_security.middleware import USER_GROUP_IDS


class DataSetAdmin(admin.ModelAdmin):
    model = DataSet


class UserGroupAdminForm(ModelForm):
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
    model = UserGroup
    form = UserGroupAdminForm
    list_display = ('name', 'manager_info', 'number_of_members')
    search_fields = ('name', )
    filter_horizontal = ('managers', 'members')

    def queryset(self, request):
        """Limit user groups to those you manage."""
        qs = super(UserGroupAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id__in=request.user.managed_user_groups.all())


class PermissionMapperAdmin(admin.ModelAdmin):
    model = PermissionMapper
    list_display = ('name', 'data_set', 'permission_group')
    list_editable = ('data_set', 'permission_group')
    list_filter = ('data_set', 'permission_group')
    search_fields = ('name', 'data_set__name')


class SecurityFilteredAdmin(admin.ModelAdmin):

    def available_permissions(self):
        user_group_ids = getattr(tls_request, USER_GROUP_IDS, None)
        if user_group_ids:
            permissions = Permission.objects.filter(
                group__permissionmapper__user_group__id__in=user_group_ids)
            permissions = [(perm.content_type.app_label + '.' + perm.codename)
                           for perm in permissions]
            return permissions
        return []

    def has_add_permission(self, request):
        """
        Returns True if the given request has permission to add an object.
        Can be overriden by the user in subclasses.
        """
        opts = self.opts
        perm = opts.app_label + '.' + opts.get_add_permission()
        if request.user.has_perm(perm):
            return True
        return perm in self.available_permissions()

    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overriden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        opts = self.opts
        perm = opts.app_label + '.' + opts.get_change_permission()
        # TODO: object permissions
        if request.user.has_perm(perm):
            return True
        result = perm in self.available_permissions()
        print "%r in %s: %s" % (perm, self.available_permissions(), result)
        return result

    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overriden by the user in subclasses. In such case it should
        return True if the given request has permission to delete the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to delete *any* object of the given type.
        """
        opts = self.opts
        perm = opts.app_label + '.' + opts.get_delete_permission()
        # TODO: object permissions
        if request.user.has_perm(perm):
            return True
        return perm in self.available_permissions()


admin.site.register(DataSet, DataSetAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(PermissionMapper, PermissionMapperAdmin)
