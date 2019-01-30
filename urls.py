from django.urls import path

from . import views
from . import ajax

urlpatterns = [
    path('', views.index, name='index'),
    path('item/create', views.item, name='item'),
    path('item/estimate', views.estimate, name='estimate'),
    path('item/new', ajax.new),
    path('item/getJson', ajax.getJson),
    path('sendOffer', ajax.sendOffer),
    path('createItem',ajax.createItem),
    path('item/exportDXF',ajax.exportDXF),
    ]
