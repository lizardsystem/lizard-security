from django.shortcuts import render

from lizard_security.testcontent.models import Content
from lizard_security.models import DataSet
from lizard_security.models import PermissionMapper
from lizard_security.models import UserGroup


def overview(request):
    user_groups = UserGroup.objects.filter(id__in=request.user_group_ids)
    permission_mappers = PermissionMapper.objects.filter(
        user_group__id__in=request.user_group_ids)
    data_sets = DataSet.objects.filter(id__in=request.allowed_data_set_ids)
    context = {
        'user': request.user,
        'data_sets': data_sets,
        'permission_mappers': permission_mappers,
        'user_groups': user_groups,
        'all_content': Content.objects.all(),
        }
    return render(request, 'testcontent/overview.html', context)

