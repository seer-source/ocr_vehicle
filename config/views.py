import copy
import csv
from datetime import datetime
import io
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from app_resources.models import Cameras, Persons
from config.forms import AddDurationForm, AddSheftForm, ConfigForm, DepartmentForm, PermissionForm,WhenForm
from config.models import AddDuration, Config, Nabatshieh, Permission, Reasons
from dashboard.models import Department
import xlrd
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.views.generic.list import ListView
from app_resources.views import cameras
from livefeed.utils import search_by_image_person
content_message=[]
def result_files(request):
     temp=copy.deepcopy(content_message)
     content_message.clear()
     return JsonResponse({'strings': temp})

def add_files(request):
    code=0
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            content_message.append('Start uploading file ' + uploaded_file.name)
           
            if uploaded_file.name.endswith('.csv'):
                try:
                    data = 0
                    with uploaded_file:
                        text_file = io.TextIOWrapper(uploaded_file, encoding='utf-8')
                        reader = csv.reader(text_file)
                        header = next(reader)
                       
                        content_message.append(header)
                        if header==['id','national_id','firstname','lastname','address_1','birthday','address_2','job','gender','religion','status','id_front','id_back','branch_id','face_id_id','created_at']:
                            for row in reader:
                                try:
                                    date_birth=datetime.strptime(row[5], "%d-%m-%Y")
                                except:
                                    date_birth=None
                                data=data+1
                                Persons.objects.create(name=row[2]+' '+row[3],gender='Male' if row[8]=='ذكر' else 'Female',
                                                       date_of_birth=date_birth,image='/faces/'+row[1]+'.jpg',
                                                       front_national_img=row[12].replace('/media',''),back_national_img=row[13].replace('/media',''),id_national=row[1],
                                                       job_title=row[7],address=row[4]+' '+row[6],status='whitelist',created_at=row[15],
                                                       religion=row[9],status_person=row[10])
                                content_message.append('read row '+str(data))
                        else:
                            code=1
                            content_message.append('this file not contain required column')

                    content_message.append(f'Successfully processed {data} rows from {uploaded_file.name}')
                except FileNotFoundError:
                    code=1
                    content_message.append("The CSV file was not found.")
                except Exception as e:
                    code=1
                    content_message.append(f"An error occurred: {str(e)}")
            elif uploaded_file.name.endswith('.xls'):
                workbook = xlrd.open_workbook(file_contents=uploaded_file.read())
                sheet = workbook.sheet_by_index(0)

                num_rows = sheet.nrows
                num_cols = sheet.ncols
                
                for row_index in range(num_rows):
                    row_data = []
                    for col_index in range(num_cols):
                        cell_value = sheet.cell_value(row_index, col_index)
                        row_data.append(cell_value)
                    try:
                        national_id=int(row_data[4])
                        # print(index)
                        # index=index+1
                        department, created_department = Department.objects.get_or_create(name=row_data[3], defaults={'name': row_data[3]})
                        person, created_person = Persons.objects.update_or_create(
                            defaults={'name':row_data[2],'registration_number': int(row_data[1]) if row_data[1] else None,
                                    'department': department},
                            id_national=str(national_id)
                        )

                        if created_department:
                            content_message.append(f"Department '{department.name}' was created.")
                        else:
                            content_message.append(f"Department '{department.name}' already exists.")

                        if created_person:
                            content_message.append(f"Person '{person.name}' was created or updated.")
                        else:
                            content_message.append(f"Person '{person.name}' already exists and was updated.")
                    except:
                        print("assssssssssssssssssss")
                        print(row_data[4])
            else:
                content_message.append('Only CSV,xls files are allowed.')
                return HttpResponseBadRequest('Only CSV files are allowed.')
            content_message.append('Exit '+str(code))

    return render(request, 'config/add_files.html',context={ "cameras":Cameras.objects.all(),})

def importatnted_fileds(request):
    instance=Config.objects.all().first()
    if instance:
        form=ConfigForm(instance=instance)
    else:
        form=ConfigForm()
    if request.method=='POST':
        if instance:
            form=ConfigForm(instance=instance,data=request.POST)
        else:
            form=ConfigForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('/')
    return render(request,'config/important_filed.html',context={'cameras':Cameras.objects.all(),'form':form})

def sheftat(request):
    sheftat=Nabatshieh.objects.all()
    return render(request,'config/sheftat.html',context={'sheftat':sheftat})

def add_sheftat(request):
    if request.method=='POST':
       
        form=AddSheftForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("/config/sheftat")
        else:
            return render(request,'config/add_sheft.html',context={'form':form})
    else:
        form=AddSheftForm()
    return render(request,'config/add_sheft.html',context={'form':form})

def edit_sheft(request,pk):
    sheft=Nabatshieh.objects.get(id=pk)
    if request.method=='POST':
        form=AddSheftForm(instance=sheft,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("/config/sheftat")
    else:
        form=AddSheftForm(instance=sheft)
    return render(request,'config/add_sheft.html',context={'form':form})

def delete_sheft(request,pk):
    sheft=Nabatshieh.objects.get(id=pk)
    sheft.delete()
    return redirect("/config/sheftat")

def when_add(request):
    if request.method=='POST':
        form=WhenForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/config/reasons/')
        else:
            return render(request,'config/when.html',context={'form':form})
    else:
        form=WhenForm()
    return render(request,'config/when.html',context={'form':form})

def reasons(request):
    return render(request,'config/reasons.html',context={'data':Reasons.objects.all()})

def update_reason(request,pk):
    item=Reasons.objects.get(id=pk)
    if request.method=='POST':
        form=WhenForm(instance=item,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/config/reasons/')
        else:
            return render(request,'config/when.html',context={'form':form})
    else:
        form=WhenForm(instance=item)
        return render(request,'config/when.html',context={'form':form})
    
def delete_reason(request,pk):
    item=Reasons.objects.get(id=pk)
    item.delete()
    return redirect('/config/reasons/')
def add_duration(request):
    if request.method=='POST':
        form=AddDurationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/config/durations')
        else:
            return render(request,'config/add_duration.html',{'form':form})
    else:
        form=AddDurationForm()
        return render(request,'config/add_duration.html',{'form':form})

def durations(request):
    return render(request,'config/durations.html',context={'durations':AddDuration.objects.all()})

def update_duration(request,pk):
    item=AddDuration.objects.get(id=pk)
    if request.method=='POST':
        form=AddDurationForm(instance=item,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/config/durations')
        else:
            return render(request,'config/add_duration.html',{'form':form})
    else:
        form=AddDurationForm(instance=item)
        return render(request,'config/add_duration.html',{'form':form})
def delete_duration(request,pk):
    item=AddDuration.objects.get(id=pk)
    item.delete()
    return redirect('/config/durations')



class AddPermission(View):
    form_class=PermissionForm
    template_name = "config/add_permission.html"
    template_name_all='config/permissions.html'
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form=self.form_class()
        return render(request,self.template_name,context={"form":form})
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.created_by=request.user
            instance.save()
            form.save_m2m()
        return render(request,self.template_name_all,context={"permissions":Permission.objects.all()})
    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['cameras']=Cameras.objects.all()
         return context
class AddPermissionMe(AddPermission):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form=self.form_class(user=request.user)
        return render(request,self.template_name,context={"form":form})
class PermissionsList(ListView):
    model = Permission
    template_name = 'config/permissions.html'
    context_object_name = 'permissions'
    
    def _split_date(self,value):
        if 'to' in value:
            start,end=value.split(' to ')
        else :
            start,end=value,value
        return start,end
    
    def _get_today_date(self):
        today_date = datetime.now().strftime('%Y-%m-%d')
        return today_date,today_date
    
    def get_queryset(self):
        date =self.request.GET.get('date_range') 
        if date:
            start,end=self._split_date(date)
        else:
            start,end=self._get_today_date()
        queryset = Permission.objects.filter(created_at__date__range=[start, end])
        return queryset
        
    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['cameras']=Cameras.objects.all()
         return context
     
    

class EditPermission(AddPermission):
    @method_decorator(login_required)
    def get(self, request, permission_id, *args, **kwargs):
        permission = get_object_or_404(Permission, id=permission_id)
        form = self.form_class(instance=permission)
        return render(request, self.template_name, context={"form": form, "permission": permission})

    @method_decorator(login_required)
    def post(self, request, permission_id, *args, **kwargs):
        permission = get_object_or_404(Permission, id=permission_id)
        form = self.form_class(request.POST, instance=permission)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
        return render(request, self.template_name_all, context={"permissions": Permission.objects.all()})


class DeletePermission(AddPermission):
    @method_decorator(login_required)
    def get(self, request, permission_id, *args, **kwargs):
        permission = get_object_or_404(Permission, id=permission_id)
        permission.delete()
        return render(request, self.template_name_all, context={"permissions": Permission.objects.all()})
    

@method_decorator(login_required, name='dispatch')
class Deparments(ListView):
    model = Department
    template_name = 'config/departments.html'
    context_object_name = 'departments'

@method_decorator(login_required, name='dispatch')
class AddDepartments(CreateView):
    model = Department
    template_name='config/add_department.html'
    form_class=DepartmentForm
    template_name_all='config/departments.html'
    success_url = reverse_lazy('departments')

@method_decorator(login_required, name='dispatch')
class EditDepartments(UpdateView):
    model = Department
    template_name = 'config/add_department.html'
    form_class = DepartmentForm
    success_url = reverse_lazy('departments')

@method_decorator(login_required, name='dispatch')
class DeleteDepartments(DeleteView):
    model = Department
    template_name = 'config/department.html'
    success_url = reverse_lazy('departments')

    def get(self, request, *args, **kwargs):
        department_id = self.kwargs.get('pk')
        print(department_id)
        department = get_object_or_404(Department, id=department_id)
        department.delete()
        return redirect('/config/departments')

def accept_permission(request,pk):
    permission=get_object_or_404(Permission,id=pk)
    permission.change_status(value=True)
    return redirect('/config/permissions/')

def refuse_permission(request,pk):
    permission=get_object_or_404(Permission,id=pk)
    permission.change_status(value=False)
    return redirect('/config/permissions/')

def capture_image_for_search(request):
    video = cameras[-1]['camera']
    frame = video.read() 
    permissions=search_get_permissions(frame)
    cameras_all=Cameras.objects.all()
    return render(request,'config/permissions.html',context={'permissions':permissions,'cameras':cameras_all})

        
def search_get_permissions(frame):
    if frame is not None:
        id=search_by_image_person(frame)
        if id:
            permissions=Permission.objects.filter(id=id)
            return permissions
    return None

@method_decorator(login_required, name='dispatch')
class PermissionNotExecute(PermissionsList):
    template_name = 'config/permissions_not_execute.html'
    def get_queryset(self):
        date =self.request.GET.get('date_range') 
        if date:
            start,end=self._split_date(date)
        else:
            start,end=self._get_today_date()
        queryset = Permission.objects.filter(created_at__date__range=[start, end],
                                             is_accept=True,time_exc_permission=None)
        return queryset