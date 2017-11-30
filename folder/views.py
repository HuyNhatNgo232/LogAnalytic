from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from folder.models import Folder
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy

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

class MyFolder(IndexView):
    def get_queryset(self):
        print "something"
        return Folder.objects.filter(created_by=self.request.user.id)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        print "dispatch"
        return super(MyFolder, self).dispatch(*args, **kwargs)


class NewFolderView(CreateView):
    model = Folder
    fields = ['title', ]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(NewFolderView, self).form_valid(form)


class EditFolderView(UpdateView):
    model = Folder
    fields = ['title', ]

    def get_queryset(self):
        base_qs = super(EditFolderView, self).get_queryset()
        return base_qs.filter(created_by=self.request.user)


class DeleteFolderView(DeleteView):
    model = Folder
    success_url = reverse_lazy('folder_list')