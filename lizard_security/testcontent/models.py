from django.db import models
from django.contrib import admin

from lizard_security.models import DataSet


class Content(models.Model):
    """Test content.

    Just for testing lizard-security's interoperability with
    non-lizard-security  models.

    """
    name = models.CharField('name',
                            max_length=80,
                            blank=True)
    data_set = models.ForeignKey(DataSet,
                                 null=True,
                                 blank=True)

    def __unicode__(self):
        if self.data_set:
            data_set_name = self.data_set.name
        else:
            data_set_name = 'no data set'
        return '%s (%s)' % (self.name, data_set_name)


admin.site.register(Content)
