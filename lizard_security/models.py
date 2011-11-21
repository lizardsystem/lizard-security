# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

CAN_VIEW_LIZARD_DATA = 'can_view_lizard_data'


class DataSet(models.Model):
    """Grouping of data.

    Other models can have a foreign key to DataSet to indicate they're part of
    this data set.

    TODO: hierarchy?

    """
    name = models.CharField(_('name'),
                            max_length=80,
                            blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Data set')
        verbose_name_plural = _('Data sets')


class UserGroup(models.Model):
    """Managed group of users, coupling users with permissions and data sets.

    A user group has members and managers: managers can add/delete users from
    the user group.

    A user group is linked to both a data set and a permission group, giving
    its members and managers the linked permission on the linked data set.

    TODO: multiple data sets?

    TODO: no permission group means read access?

    TODO: permissions in addition to permission groups?

    TODO: single permission group OK? Helps a lot in the admin.

    """
    name = models.CharField(_('name'),
                            max_length=80,
                            blank=True)
    data_set = models.ForeignKey(DataSet,
                                 null=True,
                                 blank=True)
    permission_group = models.ForeignKey(Group,
                                         null=True,
                                         blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('User group')
        verbose_name_plural = _('User groups')
        permissions = (
            (CAN_VIEW_LIZARD_DATA, 'Can view lizard data'),
            )
