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
    # show Item chart
    url(r'^chart/(?P<pk>\d+)$', views.ItemChart.as_view(), name='item_chart'),
    # api don't understand yet
    url(r'^api/data/$', views.get_data, name='api-data'),

    url(r'^api/chart/data/$', views.ChartData.as_view()),

    # Show Time Series
    url(r'^timeseries/$', views.TimeSeries.as_view(), name='time_series'),

    url(r'^api/time/$', views.get_data, name='api-time'),

    url(r'^api/time/data/$', views.TimeSeriesData.as_view()),

    url(r'^timeseries/date/$', views.DatePickerView, name='datetime_picker'),

]
