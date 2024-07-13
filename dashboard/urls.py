from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('search-id/',SearchIDView.as_view(),name='search_id'),
    path('face-id/',FaceIdView.as_view(),name='face_id')
]
