from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib import admin

from lizard_security.manager import FilteredManager
from lizard_security.manager import FilteredGeoManager
from lizard_security.models import DataSet
from lizard_security.admin import SecurityFilteredAdmin


class ContentWithoutDataset(models.Model):
    """Test content.

    Just for testing lizard-security's interoperability with
    non-lizard-security  models.

    """
    name = models.CharField('name',
                            max_length=80,
                            blank=True)

    def __unicode__(self):
        return self.name


class Content(models.Model):
    """Test content.

    Just for testing lizard-security's interoperability with
    non-lizard-security  models.

    """
    supports_object_permissions = True
    name = models.CharField('name',
                            max_length=80,
                            blank=True)
    data_set = models.ForeignKey(DataSet,
                                 null=True,
                                 blank=True)
    objects = FilteredManager()

    def __unicode__(self):
        if self.data_set:
            data_set_name = self.data_set.name
        else:
            data_set_name = 'no data set'
        return '%s (%s)' % (self.name, data_set_name)


class ContentWithForeignKeyToContentWithDataset(models.Model):
    name = models.TextField('Some field')
    content = models.ForeignKey(Content, null=True)


class GeoContent(geo_models.Model):
    """Test geo content.

    Just for testing lizard-security's interoperability with
    non-lizard-security  models.

    """
    supports_object_permissions = True
    name = geo_models.CharField('name',
                                max_length=80,
                                blank=True)
    data_set = geo_models.ForeignKey(DataSet,
                                     null=True,
                                     blank=True)
    geometry = geo_models.GeometryField(srid=4326,
                                        null=True,
                                        blank=True)
    objects = FilteredGeoManager()

    def __unicode__(self):
        if self.data_set:
            data_set_name = self.data_set.name
        else:
            data_set_name = 'no data set'
        return '%s (%s)' % (self.name, data_set_name)


admin.site.register(Content, SecurityFilteredAdmin)
admin.site.register(GeoContent, SecurityFilteredAdmin)
