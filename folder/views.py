from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from folder.models import Folder, Item
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from folder.forms import ItemForm

# Create your views here.

####################### Folder Part ###############################

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

####################### Item Part ###############################


def add_item_to_folder(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    # get upload item here
    for fi in request.FILES:
        global file_up_name
        file_up_name = str(dict(request.FILES)[fi][0])
        print file_up_name

    form = ItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.folder = folder
        item.save()
        return redirect('folder_detail', pk=folder.pk)
    else:
        form = ItemForm()
    return render(request, 'folder/item_form.html', {'form': form})


def item_approve(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.approve()
    return redirect('folder_detail', pk=item.folder.pk)


def item_remove(request, pk):
    item = get_object_or_404(Item, pk=pk)
    folder_pk = item.folder.pk
    item.delete()
    return redirect('folder_detail', pk=folder_pk)