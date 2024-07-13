from django.urls import path
from .views import *
urlpatterns = [
    path('add_files/',add_files,name='add_files'),
    path('result_files/',result_files,name='result_files'),
    path('config/',importatnted_fileds,name='importatnted_fileds'),
    path('sheftat/',sheftat,name='sheftat'),
    path('add_sheftat/',add_sheftat,name='add_sheftat'),
    path('edit_sheft/<int:pk>/',edit_sheft,name='edit_sheft'),
    path('delete_sheft/<int:pk>/',delete_sheft,name='delete_sheft'),
    path('when_add/',when_add,name='when_add'),
    path('reasons/',reasons,name='reasons'),
    path('update_reason/<int:pk>/',update_reason,name='update_reason'),
    path('delete_reason/<int:pk>/',delete_reason,name='delete_reason'),
    path('add_duration/',add_duration,name='add_duration'),
    path('durations/',durations,name='durations'),
    path('update_duration/<int:pk>/',update_duration,name='update_duration'),
    path('delete_duration/<int:pk>/',delete_duration,name='delete_duration'),
    path('add_permission/',AddPermission.as_view(),name='add_permission'),
    path('add_permission_me/',AddPermissionMe.as_view(),name='add_permission_me'),
    path('permissions/', PermissionsList.as_view(), name='permissions'),
    path('permissions/<int:permission_id>/', EditPermission.as_view(), name='edit_permissions'),
    path('delete_permissions/<int:permission_id>/', DeletePermission.as_view(), name='delete_permissions'),
    path('departments/', Deparments.as_view(), name='departments'),
    path('add_departments/', AddDepartments.as_view(), name='add_departments'),
    path('edit_departments/<int:pk>/', EditDepartments.as_view(), name='edit_departments'),
    path('delete_departments/<int:pk>/', DeleteDepartments.as_view(), name='delete_departments'),
    path('accept_permission/<int:pk>/',accept_permission,name="accept_permission"),
    path('refuse_permission/<int:pk>/',refuse_permission,name="refuse_permission"),
    path('capture_image_for_search/',capture_image_for_search,name="capture_image_for_search"),
    path('permission_not_execute/',PermissionNotExecute.as_view(),name="permission_not_execute"),
    
]