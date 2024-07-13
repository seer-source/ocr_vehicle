from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from authentications.forms import ChangePasswordForm, GroupsForm, LoginForm, PermissionForm, UpdateForm, UserForm
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.views.generic.list import ListView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import Group,Permission

from authentications.models import User

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'authentications/login.html', context={'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            branch = form.cleaned_data.get('branches')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.branch != branch:
                    messages.error(request, 'you not include in this branch')
                else:
                    login(request, user)
                    return redirect("/")
            else:
                messages.error(request, 'may be password/email not correct')
        else:
            messages.error(request, 'check inputs')
        return render(request, 'authentications/login.html', context={'form': form})



@method_decorator(login_required, name='dispatch')
class UsersView(ListView):
    model = User
    template_name = 'authentications/users_list.html'
    context_object_name = 'users'

@method_decorator(login_required, name='dispatch')
class CreateUser(CreateView):
    template_name='authentications/create_user.html'
    model=User
    form_class=UserForm
    success_url = reverse_lazy('users')
    def form_valid(self, form):
        instance=form.save()
        instance.set_password(form.cleaned_data['password'])
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class UpdateUser(UpdateView):
    model = User
    template_name = 'authentications/edit_user.html'
    form_class = UpdateForm
    success_url = reverse_lazy('users')
    
@method_decorator(login_required, name='dispatch')
class DeleteUser(DeleteView):
    model = User
    template_name = 'authentications/users.html'
    success_url = reverse_lazy('users')

    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        user = get_object_or_404(User, id=id)
        user.delete()
        return redirect('/accounts/users')
    
class ChangePasswordView(PasswordChangeView):
    template_name = 'authentications/change_pass.html'
    success_url = reverse_lazy('users')
    form_class=ChangePasswordForm
    
    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        form = self.form_class(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/users/')
        else: 
            return render(request,self.template_name,context={'form':form})
        
class GroupsView(ListView):
    template_name='authentications/groups.html'
    model=Group
    context_object_name = 'groups'
    
class AddGroupView(CreateView):
    model=Group
    template_name='authentications/create_group.html'
    form_class=GroupsForm
    success_url = reverse_lazy('groups')

class UpdateGroupView(UpdateView):
    model=Group
    template_name='authentications/update_group.html'
    form_class=GroupsForm
    success_url = reverse_lazy('groups')
    
@method_decorator(login_required, name='dispatch')
class DeleteGroupView(DeleteView):
    model = Group
    template_name = 'authentications/groups.html'
    success_url = reverse_lazy('groups')

    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        group = get_object_or_404(Group, id=id)
        group.delete()
        return redirect('/accounts/groups')
    
class PermissionsView(ListView):
    template_name='authentications/permissions.html'
    model=Permission
    context_object_name='permissions'
    
class CreatePermission(CreateView):
    template_name='authentications/add_permission.html'
    model=Permission
    form_class=PermissionForm
    success_url=reverse_lazy('permissions_list')
    
class UpdatePermission(UpdateView):
    template_name='authentications/update_permission.html'
    model=Permission
    form_class=PermissionForm
    success_url=reverse_lazy('permissions_list')
    
    
@method_decorator(login_required, name='dispatch')
class DeletePermissionView(DeleteView):
    model = Permission
    template_name = 'authentications/permissions.html'
    success_url = reverse_lazy('permission_list')

    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        permission = get_object_or_404(Permission, id=id)
        permission.delete()
        return redirect('/accounts/permissions')
    