from django.contrib import admin

from lizard_security.models import DataSet
from lizard_security.models import UserGroup


class DataSetAdmin(admin.ModelAdmin):
    model = DataSet


class UserGroupAdmin(admin.ModelAdmin):
    model = UserGroup
    list_display = ('name', 'data_set', 'permission_group')
    list_editable = ('data_set', 'permission_group')
    list_filter = ('data_set', 'permission_group')
    search_fields = ('name', 'data_set__name', 'permission_group__name')


admin.site.register(DataSet, DataSetAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
