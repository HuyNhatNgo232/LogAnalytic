# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from folder.models import Folder, Item

# Register your models here.

admin.site.register(Folder)
admin.site.register(Item)

