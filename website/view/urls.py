from django.urls import path
from . import controller

urlpatterns = [
    path('', controller.View, name = 'home-page'),
    path('filter_list',controller.filter_list,name="filter_list"),
    path('movie', controller.navigate_to_movie, name = 'navigate_to_movie'),
    path('view_database', controller.view_database, name = 'view_database'),
]