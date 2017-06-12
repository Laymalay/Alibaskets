# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from  django.forms import ModelForm
from django.db import models
import datetime

class Basket(models.Model):
    MODE_CHOICES = (('T', 'time'),
                    ('S', 'size'),)
    name = models.CharField(max_length=30,help_text='100 characters max.')
    path = models.CharField(max_length=50)
    delta_time = models.DurationField(default=datetime.timedelta(days=1,minutes=0))
    max_size = models.IntegerField(default='10')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='T')
    date_created = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return u'%s %s %s %s %s %s %s' % (self.name, self.path,
                                          self.date_created,
                                          self.last_access,
                                          self.mode,
                                          self.delta_time,
                                          self.max_size)
    class Meta:
        ordering = ['name']


