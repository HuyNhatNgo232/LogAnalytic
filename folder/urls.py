from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='folder_list'),
    url(r'^folder/(?P<pk>\d+)$', views.FolderDetailView.as_view(), name='folder_detail'),
    # create new folder
    url(r'^folder/new/$', views.NewFolderView.as_view(), name='folder_new'),
    # edit folder
    url(r'^folder/(?P<pk>\d+)/edit/$', views.EditFolderView.as_view(), name='folder_edit'),
    # delete folder
    url(r'^post/(?P<pk>\d+)/remove/$', views.DeleteFolderView.as_view(), name='folder_remove'),
    # create new item to folder
    url(r'^folder/(?P<pk>\d+)/item/$', views.add_item_to_folder, name='add_item_to_folder'),
    # approve new item
    url(r'^item/(?P<pk>\d+)/approve/$', views.item_approve, name='item_approve'),
    # remove Item
    url(r'^item/(?P<pk>\d+)/remove/$', views.item_remove, name='item_remove'),
]
