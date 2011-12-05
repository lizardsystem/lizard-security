# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
"""
Provides middleware that sets the user groups we're a member of (based on
Django users) and that sets the data sets we have access to through the
permission mapper mechanism.

"""
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
        """Set the allowed user group ids and data set ids on the request."""
        if not hasattr(request, USER_GROUP_IDS):
            request.user_group_ids = set()
        if not hasattr(request, ALLOWED_DATA_SET_IDS):
            request.allowed_data_set_ids = set()
        request.user_group_ids = request.user_group_ids.union(
            self._user_group_ids(request))
        request.allowed_data_set_ids = request.allowed_data_set_ids.union(
            self._data_sets(request))

    def _user_group_ids(self, request):
        """Return user group ids based on Django users.

        Other middleware can set user group membership based on IP addresses
        for instance, but we only look at the user group's list of members
        (which are all Django user objects).

        """
        if request.user.is_anonymous():
            return []
        return request.user.user_group_memberships.values_list('id',
                                                               flat=True)

    def _data_sets(self, request):
        """Return data sets we have access to through user group membership.

        Other middleware can allow data set access based on other reasons, but
        we look at links from user groups to data sets through permission
        mappers. Any link at all means we implicitly have view access.

        """
        if not hasattr(request, 'user_group_ids'):
            return []
        return DataSet.objects.filter(
            permission_mappers__user_group__id__in=request.user_group_ids
            ).values_list('id', flat=True)
