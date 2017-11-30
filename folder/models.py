from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.

class Folder(models.Model):
    created_by = models.ForeignKey(User)
    created_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title