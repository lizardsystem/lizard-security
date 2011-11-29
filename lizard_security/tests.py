# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from mock import Mock
from mock import patch

from lizard_security.models import DataSet
from lizard_security.models import UserGroup
from lizard_security.models import PermissionMapper
from lizard_security.admin import UserGroupAdmin
from lizard_security.admin import UserGroupAdminForm
from lizard_security.middleware import SecurityMiddleware
from lizard_security import filter_registry
from lizard_security import filters


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
        self.root = User(email='root@example.org', username='root')
        self.root.is_superuser = True
        self.root.save()
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

    def test_admin_filtering(self):
        user_group1 = UserGroup()
        user_group1.save()
        user_group2 = UserGroup()
        user_group2.save()
        user_group1.managers.add(self.admin1)
        user_group2.managers.add(self.admin2)
        user_group1.save()
        user_group2.save()
        admin_site = AdminSite()
        model_admin = UserGroupAdmin(UserGroup, admin_site)
        # Setup above, real test comes now.
        request = Mock()
        request.user = self.root
        # Root that can see all: 2 user groups.
        self.assertEquals(model_admin.queryset(request).count(), 2)
        request = Mock()
        request.user = self.admin1
        # Admin 1 can only see user group 1.
        self.assertEquals(model_admin.queryset(request).count(), 1)

    def test_manager_is_also_member(self):
        form = UserGroupAdminForm()
        form.cleaned_data = {'managers': [self.admin1],
                             'members': [self.user1]}
        form.clean()
        self.assertListEqual(form.cleaned_data['members'],
                             [self.user1, self.admin1])


class PermissionMapperTest(TestCase):

    def test_smoke(self):
        permission_mapper = PermissionMapper(name='test')
        self.assertTrue(permission_mapper)
        self.assertTrue(unicode(permission_mapper))


class AdminInterfaceTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            'adminadmin',
            'a@a.nl',
            'adminadmin')
        self.admin.save()
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()

    def test_smoke(self):
        """Looking as admin at the admin pages should not crash them :-)"""
        client = Client()
        self.assertTrue(client.login(username='adminadmin', password='adminadmin'))
        response = client.get('/admin/lizard_security/dataset/')
        self.assertEquals(response.status_code, 200)
        response = client.get('/admin/lizard_security/permissionmapper/')
        self.assertEquals(response.status_code, 200)
        response = client.get('/admin/lizard_security/usergroup/')
        self.assertEquals(response.status_code, 200)


class MiddlewareTest(TestCase):

    def setUp(self):
        self.middleware = SecurityMiddleware()
        request_factory = RequestFactory()
        self.request = request_factory.get('/some/url')
        self.request.session = {}  # Weird that it is needed.
        self.admin1 = User(email='admin1@example.org', username='admin1')
        self.admin1.save()
        self.user1 = User(email='user1@example.org', username='user1')
        self.user1.save()
        self.user2 = User(email='user2@example.org', username='user2')
        self.user2.save()
        self.user_group1 = UserGroup(name='user_group1')
        self.user_group1.save()
        self.user_group2 = UserGroup(name='user_group2')
        self.user_group2.save()
        self.data_set1 = DataSet(name='data_set1')
        self.data_set1.save()
        self.data_set2 = DataSet(name='data_set2')
        self.data_set2.save()

    def test_user_groups_for_anonymous(self):
        self.assertEquals([], self.middleware._user_group_ids(self.request))
        self.middleware.process_request(self.request)
        self.assertEquals(self.request.user_group_ids, set([]))

    def test_data_sets_for_anonymous(self):
        self.assertListEqual([], list(self.middleware._data_sets(self.request)))
        self.middleware.process_request(self.request)
        self.assertEquals(self.request.allowed_data_set_ids, set([]))

    def test_user_groups_for_non_member(self):
        self.request.user = self.user1
        self.assertListEqual([],
                             list(self.middleware._user_group_ids(self.request)))

    def test_user_groups_for_member(self):
        self.request.user = self.user1
        self.user_group1.members.add(self.user1)
        self.user_group1.save()
        self.assertListEqual([self.user_group1.id],
                             list(self.middleware._user_group_ids(self.request)))

    def test_user_groups_append(self):
        self.request.user = self.user1
        self.user_group1.members.add(self.user1)
        self.user_group1.save()
        self.request.user_group_ids = set([42])
        self.middleware.process_request(self.request)
        self.assertSetEqual(set([42, self.user_group1.id]),
                            self.request.user_group_ids)

    def test_data_sets_for_non_member(self):
        self.request.user_group_ids = set([])
        self.assertListEqual([],
                             list(self.middleware._data_sets(self.request)))

    def test_data_sets_for_member(self):
        self.request.user = self.user1
        self.user_group1.members.add(self.user1)
        self.user_group1.save()
        self.permission_mapper1 = PermissionMapper()
        self.permission_mapper1.save()
        self.permission_mapper1.user_group = self.user_group1
        self.permission_mapper1.data_set = self.data_set1
        self.permission_mapper1.save()
        self.request.user_group_ids = set([self.user_group1.id])
        # ^^^ By hand instead of via ._user_group_ids()
        self.assertSetEqual(set([self.data_set1.id]),
                            set(self.middleware._data_sets(self.request)))

    def test_data_set_append_plus_user_group_relation(self):
        self.request.user = self.user1
        self.user_group1.members.add(self.user1)
        self.user_group1.save()
        self.permission_mapper1 = PermissionMapper()
        self.permission_mapper1.save()
        self.permission_mapper1.user_group = self.user_group1
        self.permission_mapper1.data_set = self.data_set1
        self.permission_mapper1.save()
        self.request.allowed_data_set_ids = set([42])
        self.middleware.process_request(self.request)
        self.assertSetEqual(set([42, self.data_set1.id]),
                             self.request.allowed_data_set_ids)


class FilterRegistryTest(TestCase):

    def test_settings(self):
        # In our testsettings, no LIZARD_SECURITY_FILTERS is set.
        self.assertFalse(hasattr(settings, 'LIZARD_SECURITY_FILTERS'))

    def test_filter_functions_default(self):
        # By default, our filter is registered.
        self.assertListEqual(filter_registry.filter_functions(),
                             [filters.data_set_filter])

    def test_filter_functions_corner_case(self):
        with patch('lizard_security.filter_registry.settings') as settings:
            filter_registry._filter_functions = None
            settings.LIZARD_SECURITY_FILTERS = ['no_dots']
            self.assertListEqual(filter_registry.filter_functions(),
                                 [])
            filter_registry._filter_functions = None
