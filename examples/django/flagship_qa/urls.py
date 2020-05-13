from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events', views.events, name='events'),
    path('currentEnv', views.currentEnv, name='currentEnv'),
    path('setEnv', views.setEnv, name='setEnv'),
    path('setVisitor', views.setVisitor, name='setVisitor'),
    path('sendHit', views.sendHit, name='sendHit'),
    path('getFlag/<str:name>', views.getFlag, name='getFlag'),
    path('activate/<str:name>', views.activate, name='activate')
]
