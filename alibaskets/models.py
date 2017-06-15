# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from  django.forms import ModelForm
from django.db import models
import datetime

class Basket(models.Model):
    MODE_CHOICES = (('T', 'time'),
                    ('S', 'size'),)
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=50, unique=True)
    delta_time = models.DurationField(default=datetime.timedelta(days=1, minutes=0))
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


class Task(models.Model):
    PARAMS_CHOICES = (('Remove params', (
                                        ('f', 'file'),
                                        ('d', 'empty directory'),
                                        ('r', 'nor empty directory'),
                            )
                        ),
                        ('Restore params', (
                                ('m', 'merge'),
                                ('r', 'replace'),
                            )
                        ),)
    ACTION_CHOICES = (('RM', 'remove'),
                      ('RS', 'restore'),)
    params = models.CharField(max_length=20, choices=PARAMS_CHOICES, default='file')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, default='remove')
    basket_path = models.CharField(max_length=50)
    restorename = models.CharField(max_length=30, blank=True, null=True)
    path_to_removing_file = models.CharField(max_length=50, blank=True, null=True)
    regexp = models.CharField(max_length=30, blank=True, null=True)
    task_id = models.CharField(max_length=100, null=True)
    progress = models.IntegerField(default=0, null=True )
    status = models.CharField(max_length=100,default='status')
    def __unicode__(self):
        return u'%s %s %s' % (self.action, self.basket_path, self.path_to_removing_file)
