import cv2 
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render
from django.views.decorators.http import require_GET
from app_resources.models import *
from app_resources.utils import cameras, detect_person, detect_unknown
from django.conf import settings
import cv2
import os.path
import numpy as np
from imutils.video import VideoStream
import imutils
import face_recognition
from django.conf import settings
from app_resources.utils import ids
from config.models import Reasons
from app_resources.views import release_resources
from app_resources.utils import save_image
import copy

"""
def all_cameras(request):
    camears_lisy = Cameras.objects.all()
    return render(request, 'livefeed/all.html', context={
        "title": "View Cameras",
        "sub_title": "All",
        "cameras": camears_lisy
    })


def open_camera(request, id):
    release_resources(request)
    camera = Cameras.objects.filter(id=id).first()
    return render(request, 'livefeed/live_camera.html', context={
        "cameras": Cameras.objects.all(),
        "camera": camera,
        'reasons':Reasons.objects.filter(when='الدخول' if camera.camera_type=='indoor' else 'الخروج')
    })

####################################################### 
MODEL =  "hog"  #hog "cnn"
TOLERANCE = 0.6
######################################################


# Global variable to keep track of frame skipping counters for each recognized person
skip_frames_counter = {}

# Define how many frames to skip after detecting a person
FRAMES_TO_SKIP = 30



 


camera_list=[]
cameras_object=[]
@gzip.gzip_page
@require_GET
def video_feed(request, camera_id):
    global ids
    exists=False

    for obj in ids:
         if obj['camera_id']==camera_id:
              obj['persons'].clear()
              exists=True
              break
    
    if not exists:
         ids.append({
              "camera_id":camera_id,
              "persons":[]
         })
    # with open(os.path.join(settings.MEDIA_ROOT, 'representations.pkl') , 'rb') as f:
    #     representations = pickle.load(f)
    cam = Cameras.objects.filter(id=camera_id).first()
    connection_string = cam.connection_string
    if connection_string == '0':
        connection_string = 0
    if connection_string == '1':
        connection_string = 1
    global camera_list,cameras_object
    if camera_id in camera_list: 
        index = camera_list.index(camera_id)
        cameras_object[index].stream.stop()
        del camera_list[index]
        del cameras_object[index]
    
    camera = VideoStream(connection_string)
    camera_list.append(camera_id)
    cameras_object.append(camera)
    camera.start()
    camera_list.append(camera_id)
    cameras_object.append(camera)
    cameras.append({"id":cam.id, "camera": camera})

    return StreamingHttpResponse(generate(camera), content_type='multipart/x-mixed-replace; boundary=frame')

def generate(camera):
            while True:
                frame = camera.read()
                #frame = imutils.resize(frame, WIDTH_SCALE = 320)
                if camera is None:
                     break
                if frame is None:
                    continue
                try:
                     #frame = imutils.resize(frame, width=600, height=600)
                    
                    #rgb_frame  =np.ascontiguousarray(frame[:, :, ::-1]) #frame[:, :, ::-1] #frame#[:, :, ::-1]
                    
                    #face_locations = face_recognition.face_locations(rgb_frame, model = MODEL )#))
                    #frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)
                    frame = imutils.resize(frame, width=500, height=500)
                    
                    rgb_frame  = np.ascontiguousarray(frame[:, :, ::-1]) #frame[:, :, ::-1] #frame#[:, :, ::-1]
                    #rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    face_locations = face_recognition.face_locations(rgb_frame,model = MODEL )#))number_of_times_to_upsample=2,number_of_times_to_upsample=1
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    

                    name = []
                    #print("Numbr of faces:", len(face_encodings))
                    # Loop through each face found in the unknown image
                    if len(face_encodings)<5:
                        #for face_encoding in  face_encodings:
                        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                            # See if the face is a match for the known face(s)
                            matches = face_recognition.compare_faces(settings.KNOW_FACE_ENCODINGS, face_encoding,tolerance=TOLERANCE)

                            

                            # Or instead, use the known face with the smallest distance to the new face
                            face_distances = face_recognition.face_distance(settings.KNOW_FACE_ENCODINGS, face_encoding)
                            #################################
                            min_distance = min(face_distances)
                            best_match_index = np.argmin(face_distances)
                            match_percentage = face_distances[best_match_index] / TOLERANCE
                            match_percentage = match_percentage * 100
                            match_percentage = "%" + str("{:.2f}".format(match_percentage)) 
                            print(min_distance , match_percentage)
                            if min_distance <= 0.4:
                            #######################################
                                best_match_index = np.argmin(face_distances)
                                if matches[best_match_index]:
                                    name.append(settings.KNOW_FACE_NAMES[best_match_index])
                                
                                if matches[best_match_index] :
                                    print(settings.KNOW_FACE_NAMES[best_match_index])
                                    if "_"in settings.KNOW_FACE_NAMES[best_match_index]:
                                        # Check if we should skip frames for this recognized person
                                        #f skip_frames_counter.get(settings.KNOW_FACE_NAMES[best_match_index].split("_")[0], 0) > 0:
                                            # Reduce the counter for this person and skip the detection
                                        #    skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index].split("_")[0]] -= 1
                                    # else:
                                            # Detect the person and reset the skip counter
                                        #detect_person(settings.KNOW_FACE_NAMES[best_match_index].split("_")[0],camera_id)
                                        detect_person(settings.KNOW_FACE_NAMES[best_match_index].split("_")[0],camera_id,top, right, bottom, left,frame)
                                    #     skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index].split("_")[0]] = FRAMES_TO_SKIP
                                        
                                    else:

                                        # Check if we should skip frames for this recognized person
                                        #if skip_frames_counter.get(settings.KNOW_FACE_NAMES[best_match_index], 0) > 0:
                                            # Reduce the counter for this person and skip the detection
                                        #    skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index]] -= 1
                                    # else:
                                            # Detect the person and reset the skip counter
                                         detect_person(settings.KNOW_FACE_NAMES[best_match_index],camera_id,top, right, bottom, left,frame)

                                        #    skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index]] = FRAMES_TO_SKIP
                                        #detect_person(settings.KNOW_FACE_NAMES[best_match_index],camera_id)
                                    ##print("////////////////////////////////////////////")
                                else:
                                    frame=detect_unknown(top, right, bottom, left,frame)
                                    print("unknow !!!!!!!!!!!!!!!!!!!!!")
                            else:
                                frame=detect_unknown(top, right, bottom, left,frame)
                                print("unknow !!!!!!!!!!!!!!!!!!!!!")

                    
                except Exception as e:
                        print(f"An exception occurred: {e}")
                _, jpeg = cv2.imencode('.jpg', frame)
                data = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')   """




import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# View to list all cameras
def all_cameras(request):
    cameras_list = Cameras.objects.all()
    return render(request, 'livefeed/all.html', context={
        "title": "View Cameras",
        "sub_title": "All",
        "cameras": cameras_list
    })

# View to open a specific camera
def open_camera(request, id):
    release_resources(request)
    camera = Cameras.objects.filter(id=id).first()
    return render(request, 'livefeed/live_camera.html', context={
        "cameras": Cameras.objects.all(),
        "camera": camera,
        'reasons': Reasons.objects.filter(when='الدخول' if camera.camera_type == 'indoor' else 'الخروج')
    })

# Face recognition settings
MODEL = "hog"  # or "cnn" "hog"
TOLERANCE = 0.6
FRAMES_TO_SKIP = 30
skip_frames_counter = {}
thread_pool_executor = ThreadPoolExecutor(max_workers=15)
# Global variables for camera management
camera_list = []
cameras_object = []

# Queues for threading
frame_queue = queue.Queue()
result_queue = queue.Queue()

# Face processing function
def face_processing(frame):
    if frame is None:
        return None, None
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)#np.ascontiguousarray(frame[:, :, ::-1])
    face_locations = face_recognition.face_locations(rgb_frame, model=MODEL)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    return face_locations, face_encodings


# View to handle video feed
@gzip.gzip_page
@require_GET
def video_feed(request, camera_id):
    global ids, camera_list, cameras_object

    # Check if the camera is already added
    exists = False
    for obj in ids:
        if obj['camera_id'] == camera_id:
            obj['persons'].clear()
            exists = True
            break
    
    if not exists:
        ids.append({"camera_id": camera_id, "persons": []})

    # Camera setup
    cam = Cameras.objects.filter(id=camera_id).first()
    connection_string = cam.connection_string
    if connection_string == '0':
        connection_string = 0
    elif connection_string == '1':
        connection_string = 1

    # Stop existing camera stream if it's already running
    if camera_id in camera_list: 
        index = camera_list.index(camera_id)
        cameras_object[index].stream.stop()
        del camera_list[index]
        del cameras_object[index]
    
    camera = VideoStream(connection_string)
    camera.start()
    camera_list.append(camera_id)
    cameras_object.append(camera)
    cameras.append({"id": cam.id, "camera": camera})

    def generate():
        #global camera
        while True:
            frame = camera.read()
            if camera is None:
                     break
            if frame is None:
                    continue
            try:
                exact_frame=copy.copy(frame)
                frame = imutils.resize(frame, width=320, height=320)
                #frame_queue.put(frame)
                #thread_pool_executor.submit(face_processing, frame)
                #face_locations, face_encodings = result_queue.get()
                future = thread_pool_executor.submit(face_processing, frame)
                face_locations, face_encodings = future.result()
                # Face recognition logic (as in your original code)
                # ...
                name = []
                        #print("Numbr of faces:", len(face_encodings))
                        # Loop through each face found in the unknown image
                if len(face_encodings)<5:
                            #for face_encoding in  face_encodings:
                            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                                # See if the face is a match for the known face(s)
                                matches = face_recognition.compare_faces(settings.KNOW_FACE_ENCODINGS, face_encoding,tolerance=TOLERANCE)

                                

                                # Or instead, use the known face with the smallest distance to the new face
                                face_distances = face_recognition.face_distance(settings.KNOW_FACE_ENCODINGS, face_encoding)
                                #################################

                                min_distance = min(face_distances)
                                best_match_index = np.argmin(face_distances)
                                match_percentage = face_distances[best_match_index] / TOLERANCE
                                match_percentage = match_percentage * 100
                                match_percentage = "%" + str("{:.2f}".format(match_percentage)) 
                                print(min_distance , match_percentage)
                                if min_distance <= 0.4:
                                #######################################
                                    best_match_index = np.argmin(face_distances)
                                    if matches[best_match_index]:
                                        name.append(settings.KNOW_FACE_NAMES[best_match_index])
                                    
                                    if matches[best_match_index] :
                                        print(settings.KNOW_FACE_NAMES[best_match_index])
                                        if "_"in settings.KNOW_FACE_NAMES[best_match_index]:
                                            # Check if we should skip frames for this recognized person
                                            #f skip_frames_counter.get(settings.KNOW_FACE_NAMES[best_match_index].split("_")[0], 0) > 0:
                                                # Reduce the counter for this person and skip the detection
                                            #    skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index].split("_")[0]] -= 1
                                        # else:
                                                # Detect the person and reset the skip counter
                                            #detect_person(settings.KNOW_FACE_NAMES[best_match_index].split("_")[0],camera_id)
                                            detect_person(settings.KNOW_FACE_NAMES[best_match_index].split("_")[0],camera_id,top, right, bottom, left,exact_frame)
                                        #     skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index].split("_")[0]] = FRAMES_TO_SKIP
                                            
                                        else:

                                            # Check if we should skip frames for this recognized person
                                            #if skip_frames_counter.get(settings.KNOW_FACE_NAMES[best_match_index], 0) > 0:
                                                # Reduce the counter for this person and skip the detection
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          #    skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index]] -= 1
                                        # else:
                                                # Detect the person and reset the skip counter
                                            detect_person(settings.KNOW_FACE_NAMES[best_match_index],camera_id,top, right, bottom, left,exact_frame)

                                            #    skip_frames_counter[settings.KNOW_FACE_NAMES[best_match_index]] = FRAMES_TO_SKIP
                                            #detect_person(settings.KNOW_FACE_NAMES[best_match_index],camera_id)
                                        ##print("////////////////////////////////////////////")
                                    else:
                                        frame=detect_unknown(top, right, bottom, left,frame)
                                        print("unknow !!!!!!!!!!!!!!!!!!!!!")
                                else:
                                    frame=detect_unknown(top, right, bottom, left,frame)
                                    print("unknow !!!!!!!!!!!!!!!!!!!!!")

                        
            except Exception as e:
                        print(f"An exception occurred: {e}")

            _, jpeg = cv2.imencode('.jpg', frame)
            data = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')
