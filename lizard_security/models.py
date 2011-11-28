# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lizard_security import monkey_patch

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
        ordering = ['name']


class UserGroup(models.Model):
    """Managed group of users.

    A user group has members and managers: managers can add/delete users from
    the user group.

    """
    name = models.CharField(_('name'),
                            max_length=80,
                            blank=True)
    managers = models.ManyToManyField(User,
                                      verbose_name=_('managers'),
                                      related_name='managed_user_groups',
                                      blank=True)
    members = models.ManyToManyField(User,
                                     verbose_name=_('members'),
                                     related_name='user_group_memberships',
                                     blank=True)

    def number_of_members(self):
        """Return number of members (used for the admin)."""
        return self.members.count()
    number_of_members.short_description = _('Number of members')

    def manager_info(self):
        """Return comma-separated managers (used for the admin)."""
        return ', '.join(self.managers.values_list('email', flat=True))
    manager_info.short_description = _('Managers')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('User group')
        verbose_name_plural = _('User groups')

    def save(self, *args, **kwargs):
        if self.id:
            members = self.members.all()
            for manager in self.managers.all():
                if manager not in members:
                    self.members.add(manager)
        super(UserGroup, self).save(*args, **kwargs)


class PermissionMapper(models.Model):
    """Three-way mapper from user groups to data sets and permission groups.

    A user group is linked to both a data set and a permission group, giving
    its members and managers the linked permission on the linked data set.

    TODO: no permission group means read access?

    TODO: permissions in addition to permission groups?

    """
    name = models.CharField(_('name'),
                            max_length=80,
                            blank=True)
    user_group = models.ForeignKey(UserGroup,
                                   null=True,
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
        verbose_name = _('Permission mapper')
        verbose_name_plural = _('Permission mappers')
        ordering = ['user_group', 'name']
        permissions = (
            (CAN_VIEW_LIZARD_DATA, 'Can view lizard data'),
            )



