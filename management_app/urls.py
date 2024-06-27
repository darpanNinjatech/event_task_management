from django.urls import path
from .views import EventAPI, list_of_ids

urlpatterns = [
    path('/', EventAPI.as_view(), name='list'),
    path('/ids', list_of_ids, name='id_list'),
]
