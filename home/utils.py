from datetime import datetime,timedelta

from django.forms import model_to_dict
from app_resources.models import Persons
from config.models import AddDuration, Config, Nabatshieh


def perform_detection(detected_today,include=False):
    result=[]
    time_work='08:00:00'
    config=Config.objects.all().first()
    nabatshieh=Nabatshieh.objects.all()
    durations=AddDuration.objects.all()
    persons=Persons.objects.all()
    persons_detect=[]
    if config:
        time_work=config.time_end_working
    index=0
    for person in detected_today:
        index=index+1
        if person.spend_time:
            if ',' in person.spend_time:
                person.spend_time=person.spend_time.split(',')[1].strip()
        persons_detect.append(person.person_id)
        for n in nabatshieh:
            if person.person_id in n.persions.all():
                time_start = datetime.combine(datetime.today(), n.time_start_working)
                time_end = datetime.combine(datetime.today(), n.time_end_working)
                time_work = str(time_end - time_start)
                if ',' in time_work:
                    time_work=time_work.split(',')[1].strip()
        for du in durations:
            if person.person_id in n.persions.all():
                time_work_datetime = datetime.strptime(time_work,"%H:%M:%S")
                new_time_work_datetime = time_work_datetime + timedelta(hours=int(du.num_hour_working))
                time_work = new_time_work_datetime.strftime("%H:%M:%S")
        if person.reason is None and person.spend_time:
            if difference_time(person.spend_time,time_work):
                person_dict = model_to_dict(person)
                person_dict['color'] = 'green'
                person_dict['name']=person.person_id.name
                person_dict['reason_in']="لا يوجد"
                person_dict['reason_out']="لا يوجد"
                person_dict['dep'] = person.person_id.department.name if person.person_id.department else 'لا يوجد'

                person_dict['detected_at']=person.detected_at.strftime('%d-%m-%Y %H:%M:%S') if person.detected_at else 'لا يوجد'
                person_dict['outed_at']=person.outed_at.strftime('%d-%m-%Y %H:%M:%S')  if person.outed_at else 'لا يوجد'
                person_dict['spend_time']=datetime.strptime(person.spend_time.split('.')[0] if '.' in person.spend_time else person.spend_time, "%H:%M:%S").strftime('%H:%M:%S') if person.spend_time else 'لا يوجد'
                person_dict['index']=index
                person_dict['num']=person.person_id.registration_number
                result.append(person_dict)

            else:
                person_dict = model_to_dict(person)
                person_dict['color'] = 'red'
                person_dict['name']=person.person_id.name
                person_dict['reason_in']="لا يوجد"
                person_dict['reason_out']="لا يوجد"
                person_dict['dep'] = person.person_id.department.name if person.person_id.department else 'لا يوجد'

                person_dict['detected_at']=person.detected_at.strftime('%d-%m-%Y %H:%M:%S') if person.detected_at else 'لا يوجد'
                person_dict['outed_at']=person.outed_at.strftime('%d-%m-%Y %H:%M:%S')  if person.outed_at else 'لا يوجد'
                person_dict['spend_time']=datetime.strptime(person.spend_time.split('.')[0] if '.' in person.spend_time else person.spend_time, "%H:%M:%S").strftime('%H:%M:%S') if person.spend_time else 'لا يوجد'
                person_dict['index']=index
                person_dict['num']=person.person_id.registration_number
                result.append(person_dict)
        elif person.reason is None and person.spend_time is None:
            person_dict = model_to_dict(person)
            person_dict['name']=person.person_id.name
            person_dict['reason_in']="لا يوجد"
            person_dict['reason_out']="لا يوجد"
            person_dict['dep'] = person.person_id.department.name if person.person_id.department else 'لا يوجد'

            person_dict['detected_at']=person.detected_at.strftime('%d-%m-%Y %H:%M:%S') if person.detected_at else 'لا يوجد'
            person_dict['outed_at']=person.outed_at.strftime('%d-%m-%Y %H:%M:%S')  if person.outed_at else 'لا يوجد'
            person_dict['spend_time']=datetime.strptime(person.spend_time.split('.')[0] if '.' in person.spend_time else person.spend_time, "%H:%M:%S").strftime('%H:%M:%S') if person.spend_time else 'لا يوجد'
            person_dict['index']=index
            person_dict['num']=person.person_id.registration_number
            result.append(person_dict)
        elif person.reason and person.spend_time:
            person_dict = model_to_dict(person)
            person_dict['color']='blue'
            person_dict['name']=person.person_id.name
            person_dict['reason_in']="لا يوجد"
            person_dict['reason_out']=person.reason.reason.name
            person_dict['dep'] = person.person_id.department.name if person.person_id.department else 'لا يوجد'

            person_dict['detected_at']=person.detected_at.strftime('%d-%m-%Y %H:%M:%S') if person.detected_at else 'لا يوجد'
            person_dict['outed_at']=person.outed_at.strftime('%d-%m-%Y %H:%M:%S')  if person.outed_at else 'لا يوجد'
            person_dict['spend_time']=datetime.strptime(person.spend_time.split('.')[0] if '.' in person.spend_time else person.spend_time, "%H:%M:%S").strftime('%H:%M:%S') if person.spend_time else 'لا يوجد'
            person_dict['index']=index
            person_dict['num']=person.person_id.registration_number
            result.append(person_dict)
        elif person.reason and person.spend_time is None:
            person_dict = model_to_dict(person)
            person_dict['color']='yellow'
            person_dict['name']=person.person_id.name
            person_dict['reason_out']="لا يوجد"
            person_dict['reason_in']=person.reason.reason.name
            person_dict['dep'] = person.person_id.department.name if person.person_id.department else 'لا يوجد'

            person_dict['detected_at']=person.detected_at.strftime('%d-%m-%Y %H:%M:%S') if person.detected_at else 'لا يوجد'
            person_dict['outed_at']=person.outed_at.strftime('%d-%m-%Y %H:%M:%S')  if person.outed_at else 'لا يوجد'
            person_dict['spend_time']=datetime.strptime(person.spend_time.split('.')[0] if '.' in person.spend_time else person.spend_time, "%H:%M:%S").strftime('%H:%M:%S') if person.spend_time else 'لا يوجد'
            person_dict['index']=index
            person_dict['num']=person.person_id.registration_number
            result.append(person_dict)

    if include:
        for person_ in persons:
            if person_ not in persons_detect:
                    index=index+1
                    person_dict = model_to_dict(person_)
                    # print(person_dict)
                    person_dict['color']='black'
                    person_dict['name']=person_.name
                    person_dict['reason_out']="لا يوجد"
                    person_dict['reason_in']="لا يوجد"
                    person_dict['image']='' 
                    person_dict['back_national_img']=''
                    person_dict['images']=''
                    person_dict['front_national_img']=''
                    person_dict['index']=index
                    person_dict['num']=person_.registration_number
                    if person_.department:
                        person_dict['dep']=person_.department.name
                    else:
                        person_dict['dep']='لايوجد'
                    person_dict['detected_at']='لا يوجد'
                    result.append(person_dict)
            
    return result


def difference_time(spend_time_str,max_time_str):
    if ','  in spend_time_str:
        spend_time_str=spend_time_str.split(',')[1].strip()
    if '.' in spend_time_str: 
          spend_time_str=spend_time_str.split('.')[0].strip()
    if  isinstance(max_time_str, str):
        if ','  in max_time_str:
            max_time_str=max_time_str.split(',')[1].strip()
        if '.' in spend_time_str: 
            max_time_str=max_time_str.split('.')[0].strip()
    spend_time = datetime.strptime(spend_time_str, "%H:%M:%S").time()
    if isinstance(max_time_str,str):
        max_time = datetime.strptime(max_time_str, "%H:%M:%S").time()
    else:
        max_time=max_time_str
    time_difference = timedelta(
        hours=spend_time.hour,
        minutes=spend_time.minute,
        seconds=spend_time.second
    )
    time_working=timedelta(
        hours=max_time.hour,
        minutes=max_time.minute,
        seconds=max_time.second
    )
    return time_difference >= time_working