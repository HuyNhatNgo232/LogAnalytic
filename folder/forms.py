from django import forms
from .models import Folder, Item

from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm
from datetimewidget.widgets import DateTimeWidget


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ('created_by', 'title', 'created_date')


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'user_item',)


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class DatePickerForm(forms.Form):
    start = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
    end = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))

    class Meta:
        fields = ['start', 'end', ]
