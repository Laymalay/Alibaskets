# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-15 18:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alibaskets', '0008_auto_20170615_2101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='result',
        ),
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.CharField(default='status', max_length=100),
        ),
    ]