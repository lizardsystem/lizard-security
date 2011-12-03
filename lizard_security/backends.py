# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt
# -*- coding: utf-8 -*-
from django.contrib.auth.models import Permission
from tls import request

from lizard_security.middleware import USER_GROUP_IDS


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
        """Check if obj is public or if we've got extra rights to the program.
        """
        # if perm not in [CAN_VIEW_MEASURE, CAN_VIEW_PROGRAMFILE]:
        #     return False
        if obj is None:
            # Check via usergroup.
            return
        print "--- Quering perm %s for obj %s" % (perm, obj)
        # if not (isinstance(obj, Measure) or isinstance(obj, ProgramFile)):
        #     # We just deal with measures and program files.
        #     return False
        # if user.is_authenticated():
        #     if isinstance(obj, Measure):
        #         # We can access private measures if we can access at least one
        #         # program. It does *not* need to be the measure's program.
        #         has_access_to_any_program = user.profile.programs.exists()
        #         return has_access_to_any_program
        #     if isinstance(obj, ProgramFile):
        #         # We can access private programfiles only if we have access to
        #         # exactly that program.
        #         return obj.program in user.profile.programs.all()
        return False

    def has_module_perms(self, user_obj, app_label):
        """Return True if user_obj has any permissions in the given app_label.

        We only have to answer True for permissions that the user has through
        the permission mappers.

        This method is called by Django's admin

        """
        print "searching module perms for", app_label
        if app_label == 'lizard_security':
            # We need to grant access for user group managers.
            if user_obj.managed_user_groups.count():
                print "Granting module perms for", app_label
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
                    print "Granting module perms for", app_label
                    return True
        print "NOT granting module perms for", app_label
        return False
