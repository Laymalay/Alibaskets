# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-16 13:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alibaskets', '0012_auto_20170616_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_force',
            field=models.BooleanField(default=False),
        ),
    ]
