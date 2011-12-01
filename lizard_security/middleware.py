# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from lizard_security.models import DataSet

USER_GROUP_IDS = 'user_group_ids'
ALLOWED_DATA_SET_IDS = 'allowed_data_set_ids'


class SecurityMiddleware(object):
    """Add set of our user groups and accessible data sets to the request.

    Of both user groups and data sets, only the IDs are stored, not the full
    objects. We'll need to cache them, which is easier with IDs. And most of
    the time we only need the IDs anyway.

    If another middleware already added ``user_group_ids`` or
    ``allowed_data_set_ids`` to the request, those values are only added
    to. So multiple middleware can be used to set user group membership, for
    instance.

    """
    def process_request(self, request):
        if not hasattr(request, USER_GROUP_IDS):
            request.user_group_ids = set()
        if not hasattr(request, ALLOWED_DATA_SET_IDS):
            request.allowed_data_set_ids = set()
        request.user_group_ids = request.user_group_ids.union(
            self._user_group_ids(request))
        request.allowed_data_set_ids = request.allowed_data_set_ids.union(
            self._data_sets(request))

    def _user_group_ids(self, request):
        if request.user.is_anonymous():
            return []
        return request.user.user_group_memberships.values_list('id',
                                                               flat=True)

    def _data_sets(self, request):
        if not hasattr(request, 'user_group_ids'):
            return []
        return DataSet.objects.filter(
            permission_mappers__user_group__id__in=request.user_group_ids
            ).values_list('id', flat=True)
