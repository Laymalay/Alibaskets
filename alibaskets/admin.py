# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from alibaskets.models import Basket, Task


class BasketAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'date_created')
    search_fields = ('name', 'date_created')
    list_filter = ('date_created',)
    date_hierarchy = 'date_created'
    ordering = ('last_access', 'date_created')
    fields = ('name', 'path') #change the fields which could be edited
admin.site.register(Basket, BasketAdmin)
admin.site.register(Task)
