from django.contrib import admin

from lizard_security.models import DataSet
from lizard_security.models import UserGroup
from lizard_security.models import PermissionMapper


class DataSetAdmin(admin.ModelAdmin):
    model = DataSet


class UserGroupAdmin(admin.ModelAdmin):
    model = UserGroup
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


admin.site.register(DataSet, DataSetAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(PermissionMapper, PermissionMapperAdmin)
