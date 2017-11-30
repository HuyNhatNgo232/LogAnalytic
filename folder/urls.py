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
]
