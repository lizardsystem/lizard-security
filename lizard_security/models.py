# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-
"""
Lizard-security's main mechanism works through data sets, user groups and
permission mappers. These are all objects in the database, allowing management
of the security mechanism through Django's admin.

That is, until you start doing weird things in middleware like setting data
set ids based on IP numbers. Until then, everything works through the models
in this file.

"""
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lizard_security import manager

CAN_VIEW_LIZARD_DATA = 'can_view_lizard_data'


class DataOwner(models.Model):
    """Owner of the data.

    An organization, for example.

    """
    name = models.CharField(
        max_length=256,
        verbose_name=_('name'),
        unique=True,
    )
    data_managers = models.ManyToManyField(
        User,
        blank=True,
        verbose_name=_('managers')
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_('remarks')
    )

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('data owner')
        verbose_name_plural = _('data owners')


class DataSet(models.Model):
    """Grouping of data.

    Other models can have a foreign key to DataSet to indicate they're part of
    this data set.

    """
    objects = manager.DataSetManager()

    owner = models.ForeignKey(
        DataOwner,
        blank=True,
        null=True,
        verbose_name=_('owner'),
    )
    name = models.CharField(
        _('name'),
        max_length=80,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['owner', 'name']
        unique_together = ('owner', 'name')
        verbose_name = _('data set')
        verbose_name_plural = _('data sets')


class UserGroup(models.Model):
    """Managed group of users.

    A user group has members and managers: managers can add/delete users from
    the user group.

    """
    supports_object_permissions = True
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
        """Return comma-separated managers (used for the admin).

        Managers need to be staff members and need to have the global
        permission to manage user groups. If that is not the case, we include
        a warning after the username.

        """
        managers = []
        for manager in self.managers.all():
            text = manager.username
            if not manager.is_staff:
                text += ' (NOT STAFF YET)'
            if not manager.has_perm(
                'lizard_security.change_usergroup'):
                text += ' (NO GLOBAL PERM TO CHANGE USERGROUP YET)'
            managers.append(text)
        return ', '.join(managers)
    manager_info.short_description = _('Managers')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _('User group')
        verbose_name_plural = _('User groups')


class PermissionMapper(models.Model):
    """Three-way mapper from user groups to data sets and permission groups.

    A user group is linked to both a data set and a permission group, giving
    its members and managers the linked permission on the linked data set.

    Whether we do or do not link to a permission group: a permission mapper
    from a user group to a data set always means an implicit view
    permission. So it is OK not to set a permission group: what that means is
    that we want to grant the view permission to that data set/user group
    combination.

    """
    name = models.CharField(_('name'),
                            max_length=80,
                            blank=True)
    user_group = models.ForeignKey(UserGroup,
                                   related_name='permission_mappers',
                                   null=True,
                                   blank=True)
    data_set = models.ForeignKey(DataSet,
                                 related_name='permission_mappers',
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
