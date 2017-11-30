# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone
from .validators import validate_file_extension
import hashlib
import os



# Create your models here.

class Folder(models.Model):
    created_by = models.ForeignKey(User)
    created_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    def approve_items(self):
        return self.item.filter(approved_item=True)

    def get_absolute_url(self):
        return reverse("folder_detail", kwargs={'pk': self.pk})


class Item(models.Model):
    name = models.CharField(max_length=200)
    user_item = models.FileField(validators=[validate_file_extension])
    folder = models.ForeignKey(Folder, related_name="item", on_delete=models.CASCADE)
    approved_item = models.BooleanField(default=False)


    def approve(self):
        self.approved_item = True
        self.save()

    def get_absolute_url(self):
        return reverse("folder_list")

    def __str__(self):
        return self.name
