import base64
import os
from django.core.files.base import ContentFile

import io
import json
from datetime import datetime
import cv2
from django.db.models import Q
from django.http import HttpResponse, FileResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from config.models import Config, Reasons

from dashboard.models import Department
from smart_School import settings
from .models import Cameras, DetectReason, ImagesPerson, Information, Persons, PersonsDetect
from .forms import CamerasForm, InformationsForm, PersonsForm
from .utils import cameras
import requests
from livefeed.utils import image_of_person, image_update_person
import imutils
from imutils.video import VideoStream
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
# import pandas as pd

# persons = Persons.objects.all()
# dontExits=[]
# for person in persons:
#     if person.image:
#         image_url = person.image.url

#         # Construct the absolute path to the image file on disk
#         image_path = os.path.join(settings.MEDIA_ROOT, image_url[len(settings.MEDIA_URL):])

#         # Check if the file exists
#         if os.path.exists(image_path):
#             print(f"File exists for {person.name}: {image_path}")
#         else:
#             print(f"File does not exist for {person.name}: {image_path}")
#             dontExits.append(person.name)
#     else:
#         dontExits.append(person.name)
# df = pd.DataFrame(dontExits)
# df.to_excel('non_existing_images.xlsx', index=False)
        
@login_required
def add_camera(request):
    if request.method == 'POST':
        form = CamerasForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/cameras/cameras/')
    else:
        form = CamerasForm()
        return render(request, 'camera/add_camera.html', context={
            "cameras":Cameras.objects.all(),
            "title": "Camera",
            "sub_title": "Add Camera",
            "form": form,
            "add_or_update": "add"
        })

@login_required
def all_cameras(request):
    camera_all = Cameras.objects.all()
    return render(request, 'camera/cameras.html', context={"cameras": camera_all,
                                                           "title": "Camera",
                                                           "sub_title": "Cameras",
                                                           })

@login_required
def edit_camera(request, id):
    camera = Cameras.objects.filter(id=id).first()
    if request.method == 'POST':
        form = CamerasForm(request.POST, instance=camera)
        if form.is_valid():
            form.save()
            return redirect('/cameras/cameras')
    else:
        if camera:
            form = CamerasForm(instance=camera)
            return render(request, 'camera/add_camera.html', context={
                 "cameras":Cameras.objects.all(),
                "title": "Camera",
                "form": form,
                "add_or_update": "update"
            })
        else:
            return redirect('/cameras/cameras')

@login_required
def delete_camera(request, id):
    camera = Cameras.objects.filter(id=id).first()
    if camera:
        camera.delete()
        return redirect('/cameras/cameras/')
    else:
        return redirect('/cameras/cameras/')

@login_required
def add_person(request):
    cameras_list = Cameras.objects.all()
    if request.method == 'POST':
        form = PersonsForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['type_register']=='زائر':
                inforForm=InformationsForm(request.POST)
                if inforForm.is_valid():
                    person_instance = form.save(commit=False)
                    info_intsance=inforForm.save()
                    person_instance.info=info_intsance
                    # person_instance.images=image_list
                    person_instance.save() 
                    person_instance = form.save()
                    image=request.POST.get('image')
                    if image:
                        data = json.loads(image)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.image=data_image
                        person_instance.save()
                    national_front=request.POST.get('front_national_img')
                    if national_front:
                        data = json.loads(national_front)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.front_national_img=data_image
                        person_instance.save()
                    national_back=request.POST.get('back_national_img')
                    if national_back:
                        data = json.loads(national_back)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.back_national_img=data_image
                        person_instance.save()
                    base64_images = request.POST.getlist('images')
                    for base64_image in base64_images:
                        try:
                            
                            data = json.loads(base64_image)
                            data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                            im=ImagesPerson.objects.create(image=data_image)
                            person_instance.images.add(im)
                        except:
                            pass
                    person_instance.save()
                    image_of_person(person_instance)
            else:
                    person_instance = form.save()
                    info=Information.objects.create(department=Department.objects.get(id=request.POST.get('department')))
                    person_instance.info=info
                    person_instance.save()
                    image=request.POST.get('image')
                    if image:
                        data = json.loads(image)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.image=data_image
                        person_instance.save()
                    national_front=request.POST.get('front_national_img')
                    if national_front:
                        data = json.loads(national_front)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.front_national_img=data_image
                        person_instance.save()
                    national_back=request.POST.get('back_national_img')
                    if national_back:
                        data = json.loads(national_back)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.back_national_img=data_image
                        person_instance.save()
                    base64_images = request.POST.getlist('images')
                    for base64_image in base64_images:
                    
                        try:
                            data = json.loads(base64_image)
                            data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                            im=ImagesPerson.objects.create(image=data_image)
                            person_instance.images.add(im)
                            person_instance.save()
                        except:
                            print('error')
                            pass
                    image_of_person(person_instance)
            if person_instance.type_register=='موظف':
                return redirect('/persons/empolyees/')
            else:
                return redirect('/persons/visitors/')
        else:
            return render(request, 'persons/add_persons.html', context={'form': form,
                                                                        "title": "Persons",
                                                                        "sub_title": "Add Person",
                                                                        "update_or_add": "add",
                                                                        "cameras": cameras_list
                                                                        })
    else:
        form = PersonsForm()
        inforForm=InformationsForm()
        return render(request, 'persons/add_persons.html', context={'form': form,
                                                                    "title": "Persons",
                                                                    "sub_title": "Add Person",
                                                                    "update_or_add": "add",
                                                                    "cameras": cameras_list,
                                                                    'info_form':inforForm
                                                                    })

@login_required
def edit_person(request, id):
    person = Persons.objects.filter(id=id).first()
    if request.method == 'POST':
        form = PersonsForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            if form.cleaned_data['type_register']=='زائر':
                inforForm=InformationsForm(request.POST,request.FILES, instance=person.info)
                if inforForm.is_valid():
                    person_instance = form.save()
                    info_intsance=inforForm.save()
                    person_instance.info=info_intsance
                    # person_instance.images=image_list
                    person_instance.save()
                    person_instance = form.save()
                    image=request.POST.get('image')
                    if image:
                        data = json.loads(image)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.image=data_image
                        person_instance.save()
                    national_front=request.POST.get('front_national_img')
                    if national_front:
                        data = json.loads(national_front)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.front_national_img=data_image
                        person_instance.save()
                    national_back=request.POST.get('back_national_img')
                    if national_back:
                        data = json.loads(national_back)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.back_national_img=data_image
                        person_instance.save()
                    base64_images = request.POST.getlist('images')
                    person_instance.images.clear()
                    for base64_image in base64_images:
                        try:
                            data = json.loads(base64_image)
                            data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                            im=ImagesPerson.objects.create(image=data_image)
                            person_instance.images.add(im)
                        except:
                            pass
                    person_instance.save()
                    image_of_person(person_instance)
                    if person_instance.type_register=='موظف':
                        return redirect('/persons/empolyees/')
                    else:
                        return redirect('/persons/visitors/')
            else:
                    person_instance = form.save()
                    image=request.POST.get('image')
                    if image:
                        data = json.loads(image)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.image=data_image
                        person_instance.save()
                    national_front=request.POST.get('front_national_img')
                    if national_front:
                        data = json.loads(national_front)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.front_national_img=data_image
                        person_instance.save()
                    national_back=request.POST.get('back_national_img')
                    if national_back:
                        data = json.loads(national_back)
                        data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                        person_instance.back_national_img=data_image
                        person_instance.save()
                    base64_images = request.POST.getlist('images')
                    person_instance.images.clear()
                    print(base64_images)
                    for base64_image in base64_images:
                        try:
                            data = json.loads(base64_image)
                            data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                            im=ImagesPerson.objects.create(image=data_image)
                           
                            person_instance.images.add(im)
                        except:
                            print("eroor")
                            pass
                    person_instance.save()
            image_update_person(person_instance)
            if person_instance.type_register=='موظف':
                return redirect('/persons/empolyees/')
            else:
                return redirect('/persons/visitors/')
    else:
        if person:

            form = PersonsForm(instance=person,
                               initial={'image':'', 'front_national_img': '','back_national_img': '',})
            info_form=InformationsForm(instance=person.info)
           
            return render(request, 'persons/add_persons.html', context={
                "title": "تعديل بيانات الشخص",
                "form": form,
                "update_or_add": "تحديث",
                "cameras": Cameras.objects.all(),
                "person": person,
                "info_form":info_form,
                'ids_camera': person.allowed_cameras.all().values_list('id', flat=True)
            })
        else:
            return redirect('/')

@login_required
def visitors(request):
    persons_list = Persons.objects.filter(type_register='زائر')
    return render(request, 'persons/persons.html', context={"persons": persons_list, "title": "visitors",
                                                             "cameras":Cameras.objects.all(),
                                                            "sub_title": "visitors", })
@login_required
def empolyees(request):
    persons_list = Persons.objects.filter(type_register='موظف')
    return render(request, 'persons/persons.html', context={"persons": persons_list, "title": "empolyees",
                                                             "cameras":Cameras.objects.all(),
                                                            "sub_title": "empolyees", })



@login_required
def delete_person(request, id):
    person = Persons.objects.filter(id=id).first()

    if person:
        delete_representation(person)
        type_register=person.type_register
        person.delete()

    if type_register=='موظف':
        return redirect('/persons/empolyees/')
    else:
        return redirect('/persons/visitors/')

def delete_representation(person):
    pass
    # pickle_file_path = os.path.join(settings.MEDIA_ROOT, 'representations.pkl')

    # if os.path.exists(pickle_file_path):
    #     with open(pickle_file_path, "rb") as f:
    #         representations = pickle.load(f)
    #         representations = [rep for rep in representations if rep[2] != person.id]  # Remove person's representation
    #     with open(pickle_file_path, "wb") as f:
    #         pickle.dump(representations, f)
    #         print(len(representations))

@login_required
def view_person(request, id):
    person = Persons.objects.filter(id=id).first()
    report = False
    if request.method == 'POST':
        report = True
        date_range = request.POST.get('date_renge')
        start_date_str, end_date_str = date_range.split(' - ')

        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()

        detections = PersonsDetect.objects.filter(person_id=person, detected_at__range=(start_date, end_date))
    else:
        detections = PersonsDetect.objects.filter(person_id=person)
    return render(request, 'persons/profile_person.html',
                  context={"person": person, "report": report, "title": "Persons", 'detections': detections,
                            "cameras":Cameras.objects.all(),})

@login_required
def capture_image(request): 
    video = cameras[-1]['camera']
    frame = video.read()
    if frame is not None:
        ret, buffer = cv2.imencode('.jpg', frame)

        image_bytes = buffer.tobytes()

        file_object = io.BytesIO(image_bytes)

        response = FileResponse(
            file_object,
            content_type='image/jpeg',
        )
        response['Content-Disposition'] = 'attachment; filename="captured_image.jpg"'
        return response
    else:
        return HttpResponse(status=204)

@login_required
def release_resources(request): 
    try:
        for camera in cameras:
            camera['camera'].stream.release()
    except:
        pass
    return HttpResponse('done')

@login_required
def release_camera(request, id):
    try:
        for camera in cameras:
            if camera['id'] == id:
                camera['camera'].stream.release()
    except:
        pass
    return HttpResponse('done')

@login_required
@require_GET
def video_feed(request, camera_id):
    cam = Cameras.objects.filter(id=camera_id).first()
    if not cam:
        return HttpResponse("Camera not found", status=404)
    connection_string = cam.connection_string
    if connection_string == '0':
        connection_string = 0
    if connection_string == '1':
        connection_string = 1
    

    camera = VideoStream(connection_string)
    camera.start()

    cameras.append({"id": cam.id, "camera": camera})

    def stream_generator():
        try:
            while True:
                frame = camera.read()
                if frame is None:
                    continue
                frame = imutils.resize(frame, width=1000, height=1000)
                _, jpeg = cv2.imencode('.jpg', frame)
                data = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
        except GeneratorExit:
            camera.stop()

    return StreamingHttpResponse(stream_generator(), content_type='multipart/x-mixed-replace; boundary=frame')

@login_required
def get_details_from_national_img(request):
    if request.method == 'POST':
        picture = request.FILES.get('image')
        api_url = Config.objects.all().first().url_extract_data
        files = {'file': ('filename.jpg', picture.read(), 'image/jpeg')}
        response = requests.post(api_url, files=files)
        response_json = json.loads(response.text)
        image_url = Config.objects.all().first().url_image+response_json.get('face_photo')[1:]
        headers = {'Origin': '*'}

        response2 = requests.get(image_url, headers=headers)

        response_data = {
            "response": response.text,
            "image": base64.b64encode(response2.content).decode('utf-8')
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")
@login_required
def get_details_from_back_national_img(request):
    if request.method == 'POST':
        picture = request.FILES.get('image')
        api_url = Config.objects.all().first().url_extract_data_back
        files = {'file': ('filename.jpg', picture.read(), 'image/jpeg')}
        response = requests.post(api_url, files=files)
        response_json = json.loads(response.text)
        print(response_json)
        response_data = {
            "response": response.text
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def add_reason(request):
    try:
        reason = DetectReason.objects.create(
            reason=Reasons.objects.get(id=request.POST.get('id_reason', None)),
            note=request.POST.get('text', None),
            code=request.POST.get('code',None),
            # date=request.POST.get('date',None),
        )
        detect = PersonsDetect.objects.get(id=int(request.POST.get('id_detect', '')))
        detect.reason = reason
        detect.save()
        return HttpResponse(json.dumps({'result': True}), content_type="application/json")
    except Exception as e:
        print(str(e))
        return HttpResponse(json.dumps({'result': False, 'error': str(e)}), content_type="application/json")