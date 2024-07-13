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
import copy
import queue
from concurrent.futures import ThreadPoolExecutor
import pickle
import os
import os.path
import pickle
import face_recognition
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

current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, "trained_knn_model.clf")

#model_path="trained_knn_model.clf"
with open(model_path, 'rb') as f:
    knn_clf = pickle.load(f)



def predict(X_face_locations , faces_encodings, knn_clf, distance_threshold=0.5):
    
    if len(X_face_locations) == 0:
        return []

    # Use the KNN model to find the best matches for the test face
    #closest_distances = knn_clf.kneighbors([faces_encodings[0:2]], n_neighbors=2)
    #are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(2)]
    closest_distances = knn_clf.kneighbors(faces_encodings[0:2], n_neighbors=2)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(faces_encodings[0:2]))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

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
                detect_person("jdjjdj",camera_id,57, 68, 68, 68,exact_frame)
                frame = imutils.resize(frame, width=320, height=320) #face_recognition.load_image_file(os.path.join(current_dir,"test/9.jpg")) #
                #frame_queue.put(frame)
                #thread_pool_executor.submit(face_processing, frame)
                #face_locations, face_encodings = result_queue.get()
                future = thread_pool_executor.submit(face_processing, frame)
                face_locations, face_encodings = future.result()
                
                
                model_s ="knn"
                if model_s =="knn":
                    predictions = predict(face_locations, face_encodings,knn_clf, distance_threshold=0.5)
                    i=0
                    for name, _ in predictions:
                        top, right, bottom, left = face_locations[i]
                        if name =="unknown":
                            frame=detect_unknown(top, right, bottom, left,frame)
                        else:


                            if "_" in name:   
                                detect_person(name.split("_")[0],camera_id,top, right, bottom, left,frame)
                            else:
                                detect_person(name,camera_id,top, right, bottom, left,frame)
                             
                        print("- Found {}".format(name))
                        i = i+1

                else:
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
