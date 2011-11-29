from django.contrib import admin
from django.forms import ModelForm

from lizard_security.models import DataSet
from lizard_security.models import UserGroup
from lizard_security.models import PermissionMapper


class DataSetAdmin(admin.ModelAdmin):
    model = DataSet


class UserGroupAdminForm(ModelForm):
    class Meta:
        model = UserGroup

    def clean(self):
        """Make sure all managers are also members."""
        for manager in self.cleaned_data['managers']:
            if manager not in self.cleaned_data['members']:
                self.cleaned_data['members'].append(manager)
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


admin.site.register(DataSet, DataSetAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(PermissionMapper, PermissionMapperAdmin)
