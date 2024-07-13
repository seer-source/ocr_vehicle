from django.urls import path
from .views import *
urlpatterns = [
   path('report/',report,name="report"),
   path('report_visitor/',report_visitor,name="report_visitor"),
   path('load_data/<str:date>/',load_data,name="load_data"),
   path('load_data_visitor/<str:date>/',load_data_visitor,name="load_data_visitor"),
]
