from django.urls import path
from .views import *
urlpatterns = [
    path('detect/<int:camera_id>/',verticle_camera,name='detect_vehicle'),
    path('open_camera/<int:id>/',open_camera,name='vehicle_open_camera')
]