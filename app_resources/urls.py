from django.urls import path
from .views import *

url_cameras = [
    path('add_camera/',add_camera,name="add_camera"),
    path('cameras/',all_cameras,name="cameras"),
    path('edit_camera/<int:id>/',edit_camera,name="edit_camera"),
    path('delete_camera/<int:id>/',delete_camera,name="delete_camera"),
    path('release/',release_resources,name="release"),
    path('capture_image/',capture_image,name="capture_image"),
    path('release_camera/<int:id>',release_camera,name="release_camera"),
    path('video/<int:camera_id>', video_feed, name="video"),
]
url_persons= [
    path('empolyees/',empolyees,name="empolyees"),
    path('visitors/',visitors,name="visitors"),
    path('add_person/',add_person,name="add_person"),
    path('edit_person/<int:id>',edit_person,name="edit_person"),
    path('delete_person/<int:id>',delete_person,name='delete_person'),
    path('view_person/<int:id>',view_person,name="view_person"),
    path('get_details_from_national_img/',get_details_from_national_img,name="get_details_from_national_img"),
    path('get_details_from_back_national_img/',get_details_from_back_national_img,name="get_details_from_back_national_img"),
    path('add_reason/',add_reason,name="add_reason")
]

