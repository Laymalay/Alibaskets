# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-11 16:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alibaskets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='delta_time',
            field=models.DurationField(default=datetime.timedelta(0, 1200)),
        ),
    ]