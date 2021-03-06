from django.conf.urls import url, include
import notifications.urls
from . import views
app_name = 'alibaskets'
urlpatterns = [
    url(r'^$', views.basket_list, name='basket_list'),
    url(r'^basket/(?P<pk>[0-9]+)/$', views.basket_detail, name='basket_detail'),
    url(r'^task/(?P<pk>[0-9]+)/$', views.task_detail, name='task_detail'),
    url(r'^task_status/(?P<pk>[0-9]+)/$', views.task_status, name='task_status'),
    url(r'^basket/new/$', views.basket_new, name='basket_new'),
    url(r'^remove_basket/(?P<pk>[0-9]+)$', views.remove_basket, name='remove_basket'),
    url(r'^remove_task/(?P<pk>[0-9]+)$', views.remove_task, name='remove_task'),
]