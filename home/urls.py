from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
   path('',index,name="index"),
   path('school/',school,name="school"),
   path('result_cameras/<int:pk>/',result_cameras,name="result_cameras"),
   path('result_vehicle/<int:pk>/',result_vehicle,name="result_vehicle"),
   path('students/',student,name="student"),
   path('student_behevior_profile/',student_behevior_profile,name="student_behevior_profile"),
   path('show/<int:pk>/',show_table,name="show_table"),
   path('filter_camera/<str:filter_date>/<int:camera_id>',filter_camera,name="filter_camera"),
   path('logout/',logout_view,name="logout")
]
