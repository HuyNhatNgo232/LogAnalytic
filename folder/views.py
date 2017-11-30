from django.shortcuts import render
from django.views.generic import ListView
from folder.models import Folder
# Create your views here.

class IndexView(ListView):
    template_name = 'folder/index.html'
    context_object_name = 'folder_list'

    def get_queryset(self):
        return Folder.objects.all()
