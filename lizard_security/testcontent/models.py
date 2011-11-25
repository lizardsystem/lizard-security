from django.db import models

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
        return self.name
