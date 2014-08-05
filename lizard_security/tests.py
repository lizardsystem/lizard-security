# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from mock import Mock
from mock import patch

from lizard_security.admin import UserGroupAdmin
from lizard_security.admin import UserGroupAdminForm
from lizard_security.backends import LizardPermissionBackend
from lizard_security.middleware import SecurityMiddleware
from lizard_security.models import DataSet
from lizard_security.models import PermissionMapper
from lizard_security.models import UserGroup
from lizard_security.testcontent import models as testmodels
from lizard_security.testcontent.models import ContentWithoutDataset
from lizard_security.testcontent.models import Content
from lizard_security.testcontent.models import GeoContent
from lizard_security import manager as geo_manager


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
        user_group.save()
        self.assertIn('admin1', user_group.manager_info())
        self.assertNotIn('admin2', user_group.manager_info())
        self.assertIn('NOT STAFF YET', user_group.manager_info())
        self.admin1.is_staff = True
        self.admin1.save()
        self.assertNotIn('NOT STAFF YET', user_group.manager_info())
        self.assertIn('NO GLOBAL PERM', user_group.manager_info())
        self.admin1.is_staff = True
        change_permission = Permission.objects.get(codename='change_usergroup')
        self.admin1.user_permissions.add(change_permission)
        self.admin1.save()
        self.assertNotIn('NO GLOBAL PERM', user_group.manager_info())

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
        permission_mapper.save()
        self.assertTrue(permission_mapper)
        self.assertTrue(unicode(permission_mapper))

    def test_no_filtering(self):
        # We have a data_set link, but we don't actually want to be filtered
        # ourselves as we need to be queried to determin the data_set
        # access. Chicken-egg problem. (Which only surfaces when debugging,
        # btw.)
        data_set1 = DataSet(name='data_set1')
        data_set1.save()
        permission_mapper = PermissionMapper(name='test')
        permission_mapper.save()
        permission_mapper.data_set = data_set1
        permission_mapper.save()
        self.assertListEqual(list(PermissionMapper.objects.all()),
                             [permission_mapper])


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
        self.manager = User.objects.create_user(
            'managermanager',
            'a@a.nl',
            'managermanager')
        self.manager.save()
        self.manager.is_staff = True
        self.manager.save()
        self.user_group = UserGroup()
        self.user_group.save()

    def test_smoke(self):
        """Looking as admin at the admin pages should not crash them :-)"""
        client = Client()
        self.assertTrue(client.login(username='adminadmin',
                                     password='adminadmin'))
        response = client.get('/admin/')
        self.assertEquals(response.status_code, 200)
        response = client.get('/admin/lizard_security/dataset/')
        self.assertEquals(response.status_code, 200)
        response = client.get('/admin/lizard_security/permissionmapper/')
        self.assertEquals(response.status_code, 200)
        response = client.get('/admin/lizard_security/usergroup/')
        self.assertEquals(response.status_code, 200)

    def test_partial_manager(self):
        """A manager of just some bits of test content should get in, too."""
        client = Client()
        self.assertTrue(client.login(username='managermanager',
                                     password='managermanager'))
        response = client.get('/admin/testcontent/content/')
        # Permission denied as we don't have user group access.
        self.assertEquals(response.status_code, 403)
        # Now add content. Still no access.
        self.user_group.members.add(self.manager)
        self.user_group.save()
        self.data_set = DataSet(name='data_set')
        self.data_set.save()
        self.permission_mapper = PermissionMapper()
        self.permission_mapper.save()
        self.permission_mapper.user_group = self.user_group
        self.permission_mapper.data_set = self.data_set
        self.permission_mapper.save()
        self.content = Content()
        self.content.save()
        self.content.data_set = self.data_set
        self.content.save()
        response = client.get('/admin/testcontent/content/')
        self.assertEquals(response.status_code, 403)
        # Just the right permission on a group that we're not connected to
        # means nothing.
        add_permission = Permission.objects.get(codename='change_content')
        group = Group()
        group.save()
        group.permissions.add(add_permission)
        group.save()
        response = client.get('/admin/testcontent/content/')
        self.assertEquals(response.status_code, 403)
        # With rights via a user group, we ought to have access.
        self.permission_mapper.permission_group = group
        self.permission_mapper.save()
        response = client.get('/admin/testcontent/content/')
        self.assertEquals(response.status_code, 200)
        # We also see something on the main admin page.
        response = client.get('/admin/')
        self.assertEquals(response.status_code, 200)


class PermissionBackendTest(TestCase):

    def setUp(self):
        self.backend = LizardPermissionBackend()
        self.manager = User.objects.create_user(
            'managermanager',
            'a@a.nl',
            'managermanager')
        self.manager.is_staff = True
        self.manager.save()
        self.user_group = UserGroup()
        self.user_group.save()
        self.data_set = DataSet.objects.create(name='data_set')
        self.content = Content()
        self.content.data_set = self.data_set
        self.content.save()
        self.permission_mapper = PermissionMapper()
        self.permission_mapper.user_group = self.user_group
        self.permission_mapper.data_set = self.data_set
        self.permission_mapper.save()
        self.content = Content()
        self.content.data_set = self.data_set
        self.content.save()

    def test_no_authentication(self):
        self.assertEquals(None, self.backend.authenticate())

    def test_security_module_perms(self):
        """Usergroup managers need specific access to our module in de admin.
        """
        self.assertFalse(
            self.backend.has_module_perms(self.manager, 'lizard_security'))
        self.user_group.managers.add(self.manager)
        self.user_group.save()
        self.assertTrue(
            self.backend.has_module_perms(self.manager, 'lizard_security'))

    def test_has_perm_only_objects(self):
        self.assertFalse(self.backend.has_perm('dont care', 'none.can_exist'))

    def test_has_perm(self):
        add_permission = Permission.objects.get(codename='change_content')
        group = Group()
        group.save()
        group.permissions.add(add_permission)
        self.permission_mapper.permission_group = group
        self.permission_mapper.save()
        self.assertFalse(self.backend.has_perm(
            self.manager, 'testcontent.change_content', self.content))
        # If we belong to the right group, we *do* have access.
        with patch('lizard_security.backends.request') as request:
            request.user_group_ids = [self.user_group.id]
            request.allowed_data_set_ids = [self.data_set.id]
            self.assertTrue(self.backend.has_perm(
                self.manager, 'testcontent.change_content', self.content))

    def test_has_perm_with_implicit_view_perm(self):
        with patch('lizard_security.backends.request') as request:
            request.user_group_ids = [self.user_group.id]
            request.allowed_data_set_ids = [self.data_set.id]
            self.assertTrue(self.backend.has_perm(
                self.manager,
                'lizard_security.can_view_lizard_data',
                self.content))

    def test_has_perm_without_mappers(self):
        # Without any permission mappers created for this user
        self.content = Content()
        self.other_data_set = DataSet.objects.create(name='other_data_set')
        self.content.data_set = self.other_data_set
        self.content.save()
        with patch('lizard_security.backends.request') as request:
            request.user_group_ids = [self.user_group.id]
            request.allowed_data_set_ids = []
            self.assertFalse(self.backend.has_perm(
                self.manager, 'testcontent.change_content', self.content))

    def test_has_perm_with_unset_dataset(self):
        # And now with dataset is None
        add_permission = Permission.objects.get(codename='change_content')
        group = Group()
        group.save()
        group.permissions.add(add_permission)
        self.permission_mapper.permission_group = group
        self.permission_mapper.data_set = None
        self.permission_mapper.save()
        self.content.data_set = None
        self.content.save()
        self.assertFalse(self.backend.has_perm(
            self.manager, 'testcontent.change_content', self.content))
        # If we belong to the right group, we *do* have access.
        with patch('lizard_security.backends.request') as request:
            request.user_group_ids = [self.user_group.id]
            request.allowed_data_set_ids = []
            self.assertTrue(self.backend.has_perm(
                self.manager, 'testcontent.change_content', self.content))

    def test_has_perm_with_no_dataset(self):
        # And now with an object that has no dataset attribute
        add_permission = Permission.objects.get(codename='change_content')
        group = Group()
        group.save()
        group.permissions.add(add_permission)
        self.permission_mapper.permission_group = group
        self.permission_mapper.data_set = None
        self.permission_mapper.save()

        self.content = ContentWithoutDataset()
        self.content.save()
        self.assertFalse(self.backend.has_perm(
            self.manager, 'testcontent.change_content', self.content))


class MiddlewareTest(TestCase):

    def setUp(self):
        self.middleware = SecurityMiddleware()
        request_factory = RequestFactory()
        self.request = request_factory.get('/some/url')
        self.request.session = {}  # RequestFactory is bare-bones
        self.anonymous = AnonymousUser()
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
        self.request.user = self.anonymous
        self.assertEquals([], self.middleware._user_group_ids(self.request))
        self.middleware.process_request(self.request)
        self.assertEquals(self.request.user_group_ids, set([]))

    def test_data_sets_for_anonymous(self):
        self.request.user = self.anonymous
        self.assertListEqual(
            [],
            list(self.middleware._data_sets(self.request)))
        self.middleware.process_request(self.request)
        self.assertEquals(self.request.allowed_data_set_ids, set([]))

    def test_user_groups_for_non_member(self):
        self.request.user = self.user1
        self.assertListEqual(
            [],
            list(self.middleware._user_group_ids(self.request)))

    def test_user_groups_for_member(self):
        self.request.user = self.user1
        self.user_group1.members.add(self.user1)
        self.user_group1.save()
        self.assertListEqual(
            [self.user_group1.id],
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


class FilteredGeoManagerTest(TestCase):

    def setUp(self):
        self.middleware = SecurityMiddleware()
        request_factory = RequestFactory()
        self.request = request_factory.get('/some/url')
        self.user = User.objects.create_user(
            'useruser',
            'u@u.nl',
            'useruser')
        self.user.save()
        self.user_group = UserGroup(name='user_group')
        self.user_group.save()
        self.user_group.members.add(self.user)
        self.user_group.save()
        self.data_set1 = DataSet(name='data_set10')
        self.data_set1.save()
        self.data_set2 = DataSet(name='data_set20')
        self.data_set2.save()
        self.permission_mapper = PermissionMapper()
        self.permission_mapper.save()
        self.permission_mapper.user_group = self.user_group
        self.permission_mapper.data_set = self.data_set1
        self.permission_mapper.save()
        self.geo_content1 = GeoContent()
        self.geo_content1.save()
        self.geo_content1.data_set = self.data_set1
        self.geo_content1.save()
        self.geo_content2 = GeoContent()
        self.geo_content2.save()
        self.geo_content2.data_set = self.data_set2
        self.geo_content2.save()
        self.geo_content3 = GeoContent()
        self.geo_content3.save()
        self.geo_content3.data_set = None
        self.geo_content3.save()

    def test_geo_manager(self):
        request = Mock()
        request.user = self.user
        request.allowed_data_set_ids = set([self.data_set1.id])
        print request.allowed_data_set_ids
        geo_manager.request = request
        self.assertEqual(len(GeoContent.objects.all()), 2)


class ForeignKeyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'useruser',
            'u@u.nl',
            'useruser')
        self.user.save()
        self.user_group = UserGroup(name='user_group')
        self.user_group.save()
        self.user_group.members.add(self.user)
        self.user_group.save()
        self.data_set1 = DataSet(name='data_set10')
        self.data_set1.save()
        self.data_set2 = DataSet(name='data_set20')
        self.data_set2.save()

        self.permission_mapper = PermissionMapper()
        self.permission_mapper.save()
        self.permission_mapper.user_group = self.user_group
        self.permission_mapper.data_set = self.data_set1
        self.permission_mapper.save()

    def test_foreignkey_works_if_no_dataset(self):
        content = Content.objects.create(name="Some content without dataset")
        foreign = (testmodels.ContentWithForeignKeyToContentWithDataset
                   .objects.create(
                       name="Whee", content_id=content.pk))

        # Raises no exception
        self.assertTrue(foreign.content)

    def test_foreignkey_works_if_dataset_with_access(self):
        content = Content.objects.create(
            name="Some content with dataset",
            data_set=self.data_set1)
        foreign = (testmodels.ContentWithForeignKeyToContentWithDataset
                   .objects.create(
                       name="Whee", content_id=content.pk))

        # Raises no exception
        self.assertTrue(foreign.content)

    def test_foreignkey_raises_if_dataset_without_access(self):
        content = Content.objects.create(
            name="Some content with dataset but no access",
            data_set=self.data_set2)
        foreign = (testmodels.ContentWithForeignKeyToContentWithDataset
                   .objects.create(
                       name="Whee", content_id=content.pk))

        self.assertRaises(
            Content.DoesNotExist, lambda: foreign.content)
