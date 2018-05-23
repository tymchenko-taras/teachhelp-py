from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^sentence/xml$', views.sentences_xml),
    url(r'^sentence/list/$', views.SentenceView.as_view(), name='sentence/list'),
    # url(r'^post/(?P<pk>[0-9]+)/$', views.post_detail, name='post_detail'),
]