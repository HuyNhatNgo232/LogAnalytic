from django.shortcuts import render
from django.views.generic import ListView, DetailView
from folder.models import Folder
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

# Create your views here.

class IndexView(ListView):
    template_name = 'folder/index.html'
    context_object_name = 'folder_list'

    def get_queryset(self):
        return Folder.objects.all()

class FolderDetailView(DetailView):
    model = Folder
    template_name = 'folder/folder_detail.html'
    context_object_name = 'folder'