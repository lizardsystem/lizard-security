# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-

from django.test import TestCase

from lizard_security.models import DataSet


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
