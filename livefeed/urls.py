from django.urls import path
from .views import *
urlpatterns = [
   path('all/',all_cameras,name="all"),
   path('open_camera/<int:id>',open_camera,name="open_camera"),
   path('video/<int:camera_id>', video_feed, name="video"),
]
