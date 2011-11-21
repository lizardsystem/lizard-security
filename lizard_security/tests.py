# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User

from lizard_security.models import DataSet
from lizard_security.models import UserGroup


class DataSetTest(TestCase):

    def test_smoke(self):
        data_set = DataSet()
        self.assertTrue(data_set)

    def test_unicode(self):
        non_ascii_data_set = DataSet(name='täääst')
        non_ascii_data_set.save()
        id = non_ascii_data_set.id
        data_set_from_django = DataSet.objects.get(pk=id)
        self.assertTrue(unicode(data_set_from_django))


class UserGroupTest(TestCase):

    def setUp(self):
        self.admin1 = User(email='admin1@example.org', username='admin1')
        self.admin1.save()
        self.admin2 = User(email='admin2@example.org', username='admin2')
        self.admin2.save()
        self.user1 = User(email='user1@example.org', username='user1')
        self.user1.save()
        self.user2 = User(email='user2@example.org', username='user2')
        self.user2.save()

    def test_smoke(self):
        user_group = UserGroup(name='persons')
        self.assertTrue(user_group)
        self.assertTrue('persons' in unicode(user_group))

    def test_number_of_members(self):
        user_group = UserGroup()
        user_group.save()
        self.assertEquals(user_group.number_of_members(), 0)
        user_group.members.add(self.user1)
        user_group.members.add(self.user2)
        user_group.save()
        self.assertEquals(user_group.number_of_members(), 2)

    def test_manager_info(self):
        user_group = UserGroup()
        user_group.save()
        user_group.managers.add(self.admin1)
        user_group.managers.add(self.admin2)
        user_group.save()
        self.assertTrue('admin1' in user_group.manager_info())
        self.assertTrue('admin2' in user_group.manager_info())
