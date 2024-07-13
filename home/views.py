import copy
from django.contrib.auth import logout
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from django.db.models import Q
from datetime import time, timedelta, datetime
from app_resources.models import Persons, PersonsDetect, Cameras
from authentications.models import Branch
from config.models import Config, Permission
from dashboard.models import Department
from django.utils import timezone
from reports.utils import filter_persons
from home.utils import  perform_detection


# Create your views here.
@login_required
def index(request):
    cameras = Cameras.objects.all()
    now = datetime.now()
    start_time = datetime(now.year, now.month, now.day)
    time_intervals = [start_time + timedelta(hours=i) for i in range(0, 24, 2)]
    counts_day_emp = []
    counts_day_vis = []
    for i in range(len(time_intervals)):
        start_time = time_intervals[i]
        try:
            end_time = time_intervals[i + 1]
        except:
             end_time = time_intervals[11]
        count = PersonsDetect.objects.filter(
            detected_at__gte=start_time,
            detected_at__lt=end_time,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__gte=start_time,
            detected_at__lt=end_time,
            person_id__type_register='زائر'
        ).count()
        counts_day_emp.append(count)
        counts_day_vis.append(count2)
### weeee
    start_of_week = now - timedelta(days=now.weekday())
    date_intervals = [start_of_week + timedelta(days=i) for i in range(7)]
    counts_week_emp = []
    counts_week_vis = []
    for i in range(len(date_intervals)):
        start_date = date_intervals[i]
        try:
            end_date = time_intervals[i + 1]
        except:
            end_date = time_intervals[7]
        
        count = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='زائر'
        ).count()
        counts_week_emp.append(count)
        counts_week_vis.append(count2)
## month
    start_of_month = datetime(now.year, now.month, 1)
    end_of_month = start_of_month.replace(day=28) + timedelta(days=4)
    date_intervals = [start_of_month + timedelta(days=5 * i) for i in range((end_of_month - start_of_month).days // 5 + 1)]
    counts_month_emp = []
    counts_month_vis = []
    for i in range(len(date_intervals) - 1):
        start_date = date_intervals[i]
        end_date = date_intervals[i + 1]
        count = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='زائر'
        ).count()
        counts_month_emp.append(count)
        counts_month_vis.append(count2)
    #this years
    start_of_year = datetime(now.year, 1, 1)
    date_intervals = [start_of_year.replace(month=i) for i in range(1, 13)]
    counts_year_emp = []
    counts_year_vis = []
    for i in range(len(date_intervals) - 1):
        start_date = date_intervals[i]
        end_date = date_intervals[i + 1]
        count = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='زائر'
        ).count()
        counts_year_emp.append(count)
        counts_year_vis.append(count2)

    departments=Department.objects.all()
    department_counts =[]
    total_deps=0
    for dep in departments:
        count=PersonsDetect.objects.filter(
            person_id__type_register='زائر',
            person_id__info__department=dep
        ).count()
        total_deps=total_deps+count
        department_counts.append(count)
    department_counts_2 =[]
    total_deps_2=0
    for dep in departments:
        count=PersonsDetect.objects.filter(
            person_id__type_register='موظف',
            person_id__info__department=dep
        ).count()
        total_deps_2=total_deps_2+count
        department_counts_2.append(count)
    # registers = Persons.objects.filter(Q(status='whitelist') | Q(status='blacklist'))
    config=Config.objects.all().first()
    if config:
        time_exit=config.time_end_working
    else:
        time_exit=time(12,0)
    today = datetime.now().date()
    detected_at_datetime = datetime.combine(today, time_exit)
    
    activeEmpoly=PersonsDetect.objects.filter(person_id__type_register='موظف',outed_at=None).count()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)  
    one_year_ago = today - timedelta(days=365)

    active_visitor_all = PersonsDetect.objects.filter(person_id__type_register='زائر').count()
    active_visitor_today = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__date=today).count()
    active_visitor_week = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_week_ago).count()
    active_visitor_month = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_month_ago).count()
    active_visitor_year = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_year_ago).count()

    active_visitor_all_after = PersonsDetect.objects.filter(person_id__type_register='زائر',detected_at__time__gt=time_exit).count()
    active_visitor_today_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__date=today,detected_at__time__gt=time_exit).count()
    active_visitor_week_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_week_ago,detected_at__time__gt=time_exit).count()
    active_visitor_month_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_month_ago,detected_at__time__gt=time_exit).count()
    active_visitor_year_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_year_ago,detected_at__time__gt=time_exit).count()
   
    all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر',outed_at=None).count()
    active_visitor_after=PersonsDetect.objects.filter(person_id__type_register='زائر',outed_at=None,detected_at__date=today, detected_at__gt=detected_at_datetime).count()
   
    most_visitor = PersonsDetect.objects.filter(person_id__type_register='زائر')
    most_visitor = most_visitor.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_visitor = most_visitor.annotate(visits=Count('person_id'))
    most_visitor = most_visitor.order_by('-visits')[:5]

    most_visitor_after = PersonsDetect.objects.filter(person_id__type_register='زائر',detected_at__time__gt=detected_at_datetime)
    most_visitor_after = most_visitor_after.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_visitor_after = most_visitor_after.annotate(visits=Count('person_id'))
    most_visitor_after = most_visitor_after.order_by('-visits')[:5]
    
    most_empolyee = PersonsDetect.objects.filter(person_id__type_register='موظف')
    most_empolyee = most_empolyee.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_empolyee = most_empolyee.annotate(visits=Count('person_id'))
    most_empolyee = most_empolyee.order_by('-visits')[:5]

    most_visitor_dep = PersonsDetect.objects.filter(person_id__type_register='زائر')
    most_visitor_dep = most_visitor_dep.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_visitor_dep = most_visitor_dep.annotate(visits=Count('person_id__info__department'))
    most_visitor_dep = most_visitor_dep.order_by('-visits')[:5]

    detected_today=PersonsDetect.objects.filter(
    Q(person_id__type_register='موظف',
    detected_at__date=today)|Q(outed_at__date=today,person_id__type_register='موظف', detected_at=None)
    )
    #detected_today=filter_persons(detected_today)   

    detected_today = perform_detection(detected_today)
    permissions= Permission.objects.filter(created_at__date__range=[today, today])
    
   
    return render(request, 'home/index.html', context={         
                                                       'active_Empolyee':activeEmpoly,
                                                       "detected_today":detected_today,
                                                       'most_visitor':most_visitor,
                                                       "most_visitor_dep":most_visitor_dep,
                                                       "most_empolyee":most_empolyee,
                                                       "most_visitor_after":most_visitor_after,
                                                       'active_visitor_all':active_visitor_all,
                                                       'active_visitor_day':active_visitor_today,
                                                       'active_visitor_week':active_visitor_week,
                                                       'active_visitor_month':active_visitor_month,
                                                       'active_visitor_year':active_visitor_year,
                                                       "active_visitor_all_after":active_visitor_all_after,
                                                       "active_visitor_day_after":active_visitor_today_after,
                                                       "active_visitor_week_after":active_visitor_week_after,
                                                       "active_visitor_month_after":active_visitor_month_after,
                                                       "active_visitor_year_after":active_visitor_year_after,
                                                       'all_visitor':all_visitor,
                                                       'active_visitor_after':active_visitor_after,
                                                       'cameras':cameras,
                                                       'counts_day_emp':counts_day_emp,
                                                       'counts_day_vis':counts_day_vis,
                                                       'counts_week_emp':counts_week_emp,
                                                       'counts_week_vis':counts_week_vis,
                                                       'counts_month_emp':counts_month_emp,
                                                       'counts_month_vis':counts_month_vis,
                                                       'counts_year_emp':counts_year_emp,
                                                       'counts_year_vis':counts_year_vis,
                                                       'departments':departments,
                                                       'counts_department':department_counts,
                                                       'total_deps':total_deps,
                                                       'counts_department_2':department_counts_2,
                                                       'total_deps_2':total_deps_2,
                                                       'permissions':permissions
                                                       })

def result_cameras(request,pk):   
    from app_resources.utils import object_data
    resu=copy.deepcopy(object_data)
    res=[]
    for obj in object_data:
        if obj['id_camera']!=pk:
            res.append(obj)
    object_data.clear()
    object_data.extend(res)
    
    return JsonResponse({
        "data": resu
    })
    
    
def result_vehicle(request,pk):   
    from app_resources.utils import object_data_vehicle
    resu=copy.deepcopy(object_data_vehicle)
    res=[]
    for obj in object_data_vehicle:
        if obj['id_camera']!=pk:
            res.append(obj)
    object_data_vehicle.clear()
    object_data_vehicle.extend(res)
    
    return JsonResponse({
        "data": resu
    })


@login_required
def filter_camera(request, filter_date,camera_id):
    start_date_str, end_date_str = filter_date.split(" - ")
    start_date = datetime.strptime(start_date_str, "%B %d, %Y")
    end_date = datetime.strptime(end_date_str, "%B %d, %Y")
    detection_count = PersonsDetect.objects.filter(detected_at__range=(start_date, end_date),
                                                   camera_id__id=camera_id).count()
    detection_count_white = PersonsDetect.objects.filter(detected_at__range=(start_date, end_date),
                                                         camera_id__id=camera_id,
                                                         person_id__status='whitelist').count()
    detection_count_black = PersonsDetect.objects.filter(detected_at__range=(start_date, end_date),
                                                         camera_id__id=camera_id,
                                                         person_id__status='blacklist').count()
    detection_count_unknown = PersonsDetect.objects.filter(detected_at__range=(start_date, end_date),
                                                           camera_id__id=camera_id,
                                                           person_id__status='unknown').count()
    return JsonResponse({
        "detection_count": "detection_count",
        "detection_count_white": "detection_count_white",
        "detection_count_black": "detection_count_black",
        "detection_count_unknown": "detection_count_unknown"
    })


def show_table(request,pk):
    title_all=""
    all_visitor=[]
    today = datetime.now().date()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)  
    one_year_ago = today - timedelta(days=365)
    branches=None
    emp=False
    config=Config.objects.all().first()
    if config:
        time_exit=config.time_end_working
    else:
        time_exit=time(12,0)
   
    if pk==1:
        title_all='الزائرين النشط'
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر',outed_at=None)
    elif pk==2:
        title_all='الموظفون النشط'
        emp=True
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='موظف',outed_at=None)
    elif pk==3:
        title_all='كل  الزوار'
        branches=Branch.objects.all()
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر')
    elif pk==4:
        title_all=' كل  الزوار اليوم' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__date=today)
    elif pk==5:
        title_all=' كل  الزوار الاسيوع' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_week_ago)
    elif pk==6:
        title_all=' كل  الزوار الشهر' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_month_ago)
    elif pk==7:
        title_all=' كل  الزوار السنة' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_year_ago)
    elif pk==8:
        title_all=' كل  الزوار بعد ساعات العمل ' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر',detected_at__time__gt=time_exit)
    elif pk==9:
        title_all='  كل  الزوار بعد ساعات العمل اليوم ' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__date=today,detected_at__time__gt=time_exit)
    elif pk==10:
        title_all='  كل  الزوار بعد ساعات العمل الاسبوع ' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_week_ago,detected_at__time__gt=time_exit)
    elif pk==11:
        title_all='  كل  الزوار بعد ساعات العمل الشهر ' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_month_ago,detected_at__time__gt=time_exit)
    elif pk==12:
        title_all='  كل  الزوار بعد ساعات العمل السنة ' 
        all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_year_ago,detected_at__time__gt=time_exit)
    return render(request,'home/view_all.html',context={"title_all":title_all,"all_visitor":all_visitor, "cameras":Cameras.objects.all(),"branches":branches,
                                                        'emp':emp})

def student(request):
    title_all='التلاميذ النشط'
    emp=True
    branches=None
    all_visitor=PersonsDetect.objects.filter(person_id__type_register='موظف',outed_at=None)
    return render(request,'home/view_all.html',context={"title_all":title_all,"all_visitor":all_visitor, "cameras":Cameras.objects.all(),"branches":branches,
                                                        'emp':emp})
    
def student_behevior_profile(request):
    return render(request,'school/student_behevior_profile.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def school(request):
    cameras = Cameras.objects.all()
    now = datetime.now()
    start_time = datetime(now.year, now.month, now.day)
    time_intervals = [start_time + timedelta(hours=i) for i in range(0, 24, 2)]
    counts_day_emp = []
    counts_day_vis = []
    for i in range(len(time_intervals)):
        start_time = time_intervals[i]
        try:
            end_time = time_intervals[i + 1]
        except:
             end_time = time_intervals[11]
        count = PersonsDetect.objects.filter(
            detected_at__gte=start_time,
            detected_at__lt=end_time,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__gte=start_time,
            detected_at__lt=end_time,
            person_id__type_register='زائر'
        ).count()
        counts_day_emp.append(count)
        counts_day_vis.append(count2)
### weeee
    start_of_week = now - timedelta(days=now.weekday())
    date_intervals = [start_of_week + timedelta(days=i) for i in range(7)]
    counts_week_emp = []
    counts_week_vis = []
    for i in range(len(date_intervals)):
        start_date = date_intervals[i]
        try:
            end_date = time_intervals[i + 1]
        except:
            end_date = time_intervals[7]
        
        count = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='زائر'
        ).count()
        counts_week_emp.append(count)
        counts_week_vis.append(count2)
## month
    start_of_month = datetime(now.year, now.month, 1)
    end_of_month = start_of_month.replace(day=28) + timedelta(days=4)
    date_intervals = [start_of_month + timedelta(days=5 * i) for i in range((end_of_month - start_of_month).days // 5 + 1)]
    counts_month_emp = []
    counts_month_vis = []
    for i in range(len(date_intervals) - 1):
        start_date = date_intervals[i]
        end_date = date_intervals[i + 1]
        count = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='زائر'
        ).count()
        counts_month_emp.append(count)
        counts_month_vis.append(count2)
    #this years
    start_of_year = datetime(now.year, 1, 1)
    date_intervals = [start_of_year.replace(month=i) for i in range(1, 13)]
    counts_year_emp = []
    counts_year_vis = []
    for i in range(len(date_intervals) - 1):
        start_date = date_intervals[i]
        end_date = date_intervals[i + 1]
        count = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='موظف'
        ).count()
        count2 = PersonsDetect.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lt=end_date,
            person_id__type_register='زائر'
        ).count()
        counts_year_emp.append(count)
        counts_year_vis.append(count2)

    departments=Department.objects.all()
    department_counts =[]
    total_deps=0
    for dep in departments:
        count=PersonsDetect.objects.filter(
            person_id__type_register='زائر',
            person_id__info__department=dep
        ).count()
        total_deps=total_deps+count
        department_counts.append(count)
    department_counts_2 =[]
    total_deps_2=0
    for dep in departments:
        count=PersonsDetect.objects.filter(
            person_id__type_register='موظف',
            person_id__info__department=dep
        ).count()
        total_deps_2=total_deps_2+count
        department_counts_2.append(count)
    # registers = Persons.objects.filter(Q(status='whitelist') | Q(status='blacklist'))
    config=Config.objects.all().first()
    if config:
        time_exit=config.time_end_working
    else:
        time_exit=time(12,0)
    today = datetime.now().date()
    detected_at_datetime = datetime.combine(today, time_exit)
    
    activeEmpoly=PersonsDetect.objects.filter(person_id__type_register='موظف',outed_at=None).count()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)  
    one_year_ago = today - timedelta(days=365)

    active_visitor_all = PersonsDetect.objects.filter(person_id__type_register='زائر').count()
    active_visitor_today = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__date=today).count()
    active_visitor_week = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_week_ago).count()
    active_visitor_month = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_month_ago).count()
    active_visitor_year = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_year_ago).count()

    active_visitor_all_after = PersonsDetect.objects.filter(person_id__type_register='زائر',detected_at__time__gt=time_exit).count()
    active_visitor_today_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__date=today,detected_at__time__gt=time_exit).count()
    active_visitor_week_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_week_ago,detected_at__time__gt=time_exit).count()
    active_visitor_month_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_month_ago,detected_at__time__gt=time_exit).count()
    active_visitor_year_after = PersonsDetect.objects.filter(person_id__type_register='زائر', detected_at__gte=one_year_ago,detected_at__time__gt=time_exit).count()
   
    all_visitor=PersonsDetect.objects.filter(person_id__type_register='زائر',outed_at=None).count()
    active_visitor_after=PersonsDetect.objects.filter(person_id__type_register='زائر',outed_at=None,detected_at__date=today, detected_at__gt=detected_at_datetime).count()
   
    most_visitor = PersonsDetect.objects.filter(person_id__type_register='زائر')
    most_visitor = most_visitor.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_visitor = most_visitor.annotate(visits=Count('person_id'))
    most_visitor = most_visitor.order_by('-visits')[:5]

    most_visitor_after = PersonsDetect.objects.filter(person_id__type_register='زائر',detected_at__time__gt=detected_at_datetime)
    most_visitor_after = most_visitor_after.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_visitor_after = most_visitor_after.annotate(visits=Count('person_id'))
    most_visitor_after = most_visitor_after.order_by('-visits')[:5]
    
    most_empolyee = PersonsDetect.objects.filter(person_id__type_register='موظف')
    most_empolyee = most_empolyee.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_empolyee = most_empolyee.annotate(visits=Count('person_id'))
    most_empolyee = most_empolyee.order_by('-visits')[:5]

    most_visitor_dep = PersonsDetect.objects.filter(person_id__type_register='زائر')
    most_visitor_dep = most_visitor_dep.values('person_id','person_id__name','person_id__image','person_id__job_title')
    most_visitor_dep = most_visitor_dep.annotate(visits=Count('person_id__info__department'))
    most_visitor_dep = most_visitor_dep.order_by('-visits')[:5]

    detected_today=PersonsDetect.objects.filter(
    Q(person_id__type_register='موظف',
    detected_at__date=today)|Q(outed_at__date=today,person_id__type_register='موظف', detected_at=None)
    )
    #detected_today=filter_persons(detected_today)   

    detected_today = perform_detection(detected_today)
    permissions= Permission.objects.filter(created_at__date__range=[today, today])
    
   
    return render(request, 'home/school.html', context={         
                                                       'active_Empolyee':activeEmpoly,
                                                       "detected_today":detected_today,
                                                       'most_visitor':most_visitor,
                                                       "most_visitor_dep":most_visitor_dep,
                                                       "most_empolyee":most_empolyee,
                                                       "most_visitor_after":most_visitor_after,
                                                       'active_visitor_all':active_visitor_all,
                                                       'active_visitor_day':active_visitor_today,
                                                       'active_visitor_week':active_visitor_week,
                                                       'active_visitor_month':active_visitor_month,
                                                       'active_visitor_year':active_visitor_year,
                                                       "active_visitor_all_after":active_visitor_all_after,
                                                       "active_visitor_day_after":active_visitor_today_after,
                                                       "active_visitor_week_after":active_visitor_week_after,
                                                       "active_visitor_month_after":active_visitor_month_after,
                                                       "active_visitor_year_after":active_visitor_year_after,
                                                       'all_visitor':all_visitor,
                                                       'active_visitor_after':active_visitor_after,
                                                       'cameras':cameras,
                                                       'counts_day_emp':counts_day_emp,
                                                       'counts_day_vis':counts_day_vis,
                                                       'counts_week_emp':counts_week_emp,
                                                       'counts_week_vis':counts_week_vis,
                                                       'counts_month_emp':counts_month_emp,
                                                       'counts_month_vis':counts_month_vis,
                                                       'counts_year_emp':counts_year_emp,
                                                       'counts_year_vis':counts_year_vis,
                                                       'departments':departments,
                                                       'counts_department':department_counts,
                                                       'total_deps':total_deps,
                                                       'counts_department_2':department_counts_2,
                                                       'total_deps_2':total_deps_2,
                                                       'permissions':permissions
                                                       })

