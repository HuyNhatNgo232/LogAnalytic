from django import forms
from .models import Folder, Item

from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ('created_by', 'title', 'created_date')


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'user_item',)
