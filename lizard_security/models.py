# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DataSet(models.Model):
    """Grouping of data.

    Other models can have a foreign key to DataSet to indicate they're part of
    this data set.

    """
    name = models.CharField(_('name'),
                            max_length=80,
                            blank=True)

    def __unicode__(self):
        return u'<DataSet %s>' % self.name

    class Meta:
        verbose_name = _('Data set')
        verbose_name_plural = _('Data sets')
