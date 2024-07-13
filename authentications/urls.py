from django.urls import path
from .views import *
urlpatterns = [
   path('login/',LoginView.as_view(),name="login"),
   path('users/',UsersView.as_view(),name="users"),
   path('create_user/',CreateUser.as_view(),name="create_user"),
   path('update_user/<int:pk>/',UpdateUser.as_view(),name="update_user"),
   path('delete_user/<int:pk>/',DeleteUser.as_view(),name="delete_user"),
   path('change-password/<int:pk>/',ChangePasswordView.as_view(),name="change-password"),
   path('groups/',GroupsView.as_view(),name="groups"),
   path('add_group/',AddGroupView.as_view(),name="add_group"),
   path('update_group/<int:pk>/',UpdateGroupView.as_view(),name="update_group"),
   path('delete_group/<int:pk>/',DeleteGroupView.as_view(),name="delete_group"),
   path('permissions/',PermissionsView.as_view(),name="permissions_list"),
   path('create_permission/',CreatePermission.as_view(),name="create_permission"),
   path('update_permission/<int:pk>/',UpdatePermission.as_view(),name="update_permission"),
   path('delete_permission/<int:pk>/',DeletePermissionView.as_view(),name="delete_per"),
]
