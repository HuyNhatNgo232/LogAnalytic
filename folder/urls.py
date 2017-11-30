from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='folder_list'),
    url(r'^folder/(?P<pk>\d+)$', views.FolderDetailView.as_view(), name='folder_detail'),

]
