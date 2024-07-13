
from datetime import datetime
from io import BytesIO
import os
import requests
import numpy as np
from config.models import Config, Permission
from .models import PersonsDetect, Persons, Cameras, Vehicle
from PIL import Image
import cv2
import arabic_reshaper 
from bidi.algorithm import get_display 
from PIL import Image, ImageFont, ImageDraw
from django.core.files.uploadedfile import InMemoryUploadedFile
cameras = []
object_data = []
object_data_vehicle=[]
ids=[]
ids_vehicel=[]


def detect_person(national_id,camera_id,top, right, bottom, left,frame):
    config=Config.objects.first()
    try:
        camera = Cameras.objects.get(id=camera_id)
        person = Persons.objects.get(id_national=national_id)
        # save_image(person, frame)
        exist=None
        for obj in ids:
            if obj['camera_id']==camera_id and national_id in obj['persons']:
                exist=obj
                break
        if  exist is None:
            for obj in ids:
                if obj['camera_id']==camera_id:
                    obj['persons'].append(national_id)
            detect=None
            if camera.camera_type=='outdoor':
                detect=PersonsDetect.objects.filter(person_id=person,camera_id__camera_type='indoor').last()
                if detect:
                    detect.camera_id=camera
                    detect.save()
                else:
                    detect=PersonsDetect.objects.create(
                    camera_id=camera,
                    person_id=person,
                )
            else:
                detect=PersonsDetect.objects.create(
                camera_id=camera,
                person_id=person,
            )
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            permission=Permission.objects.filter(for_emp__id=person.id,created_at__date=today_start).last()
            per=None
            show=True
            if permission:
                if not permission.time_exc_permission:        
                    if permission.is_accept:
                        permission.execute()
                        if config:
                            show = config.num_end_permission > permission.time_exc_permission.total_seconds() / 3600
                        else:
                            show = 2.0 > permission.time_exc_permission.total_seconds() / 3600
                    if show:
                        if permission.reason.when=='الدخول' and camera.camera_type=='indoor':
                                        per={
                                            'title':permission.reason.name,
                                            'message':'حالة التصريح '+'لم يتم الاطلاع' if permission.is_accept==None else 'حالة التصريح '+ f'مقبول تم التنفيذ بعد  {format_time(permission.time_exc_permission)}' if  permission.is_accept  else  'حالة التصريح '+'مرفوض',
                                        'color':'warning' if permission.is_accept==None else 'success' if permission.is_accept else 'danger',
                                        }
                        elif permission.reason.when=='الخروج' and camera.camera_type=='outdoor':
                                        per={
                                            'title':permission.reason.name,
                                            'message':'حالة التصريح '+'لم يتم الاطلاع' if permission.is_accept==None else 'حالة التصريح '+ f'مقبول تم التنفيذ بعد  {format_time(permission.time_exc_permission)} ' if permission.is_accept else 'حالة التصريح '+'مرفوض',
                                            'color':'warning' if permission.is_accept==None else 'success' if permission.is_accept else 'danger',
                                        } 
                    
                        

            object_data.append({
                "id_camera":camera_id,
                "category":'green' if person.status=='whitelist' else 'red',
                "sort":'white' if person.status=='whitelist' else 'black',
                "id_person":person.id,
                "id":person.id_national,
                "name":person.name,
                "img":person.image.url,
                "des":detect.id,
                "permission":per
            })
            #sendWhatsAppMessage(person)
        color =(0, 255, 0) if person.status=='whitelist' else (55, 55, 255)
        return draw_name(top, right, bottom, left,frame,person.name,person.department.name,color)
    except Exception as e:
        print("errr:=>",e)


def detect_unknown(top, right, bottom, left,frame):
   return draw_name(top, right, bottom, left,frame,'غير معروف','',(127,255,255))

def save_image(person, frame):
    try:
        folder_path = os.path.join('media', 'detections', str(person.id_national))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        existing_items = len(os.listdir(folder_path))
        image_filename = f"{existing_items + 1}.jpg"
        image_path = os.path.join(folder_path, image_filename)
        name_path = os.path.join(folder_path, 'name.txt')
        _, jpeg = cv2.imencode('.jpg', frame)
        data = jpeg.tobytes()
        with open(image_path, 'wb') as f:
            f.write(data)
        with open(name_path, 'w') as f:
            f.write(str(person.name)+'\n'+str(person.registration_number))
    except FileNotFoundError:
        print(f"Error: The folder path '{folder_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
        


def draw_name(top, right, bottom, left,frame,text,dep,color):
    x, y, w, h = left, top, right - left, bottom - top
    draw_border(frame,(left,top),(right,bottom),color,2,10,20)
    rect_color = (128, 128, 128)  
    rect_opacity = 0.3
    overlay = frame.copy()
    cv2.rectangle(overlay, (x+w+100, y-20), (x+w+10, y+20), rect_color, -1)
    cv2.addWeighted(overlay, rect_opacity, frame, 1 - rect_opacity, 0, frame)
    font = cv2.FONT_HERSHEY_COMPLEX 
    reshaped_text = arabic_reshaper.reshape(text)
    reshaped_text2 = arabic_reshaper.reshape(dep)
    bidi_text = get_display(reshaped_text) 
    bidi_text2 = get_display(reshaped_text2) 
    font = ImageFont.truetype("sahel.ttf", size=13)
    im=Image.fromarray(frame)
    d = ImageDraw.Draw(im)
    d.multiline_text((x+w+20,y-20), bidi_text, font=font, spacing=15, align="center")
    d.multiline_text((x+w+20,y), bidi_text2, font=font, spacing=15, align="center")
    return np.array(im)

def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1,y1 = pt1
    x2,y2 = pt2
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)


def sendWhatsAppMessage(person):
    
    config=Config.objects.all().first()
    if config:
        access_token = config.token_access
        url = config.url_whatsapp
        message_data = {
        "messaging_product": "whatsapp",
        "to": f"2${person.mobile_whatsapp}",
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {"code": "en_US"}
        }
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=message_data, headers=headers)
  
def format_time(time_exc_permission):
    hours, remainder = divmod(time_exc_permission.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    return f'{hours:02}:{minutes:02}'

def detect_vehicle(camera_id,vehicle_image,label_image,label):
    # try:
        exist=None
        for obj in ids_vehicel:
            if obj['camera_id']==camera_id and label in obj['labels']:
                exist=obj
                break
        if  exist is None:
            for obj in ids_vehicel:
                if obj['camera_id']==camera_id:
                    obj['labels'].append(label)
            vehicle=Vehicle.objects.filter(label=label).first()
            if vehicle is None:
                vehicle= Vehicle.objects.create(
                        vehicle_image=save_image_from_frame(vehicle_image),
                        label_image=save_image_from_frame(label_image),
                        label=label
                )
            object_data_vehicle.append({
                "id_vehicle":vehicle.id,
                "id_camera":camera_id,
                "label":vehicle.label,
                "vehicle_image":vehicle.vehicle_image.url,
                "label_image":vehicle.label_image.url
                })   
    # except e:
    #     print(e)


def save_image_from_frame(frame):
    image_io = BytesIO()
    pil_image = Image.fromarray(frame)
    pil_image.save(image_io, format='JPEG')
    return InMemoryUploadedFile(image_io, None, 'image.jpg', 'image/jpeg', image_io.tell(), None)