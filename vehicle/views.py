

from io import BytesIO
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render
from django.views.decorators.http import require_GET
from app_resources.models import Cameras
from imutils.video import VideoStream
from app_resources.utils import cameras
import cv2
import numpy as np
import os
from PIL import Image
from vehicle.vehicle_tracker import ObjectTracker,VideoProcessor
from app_resources.utils import detect_vehicle,ids_vehicel

# from vehicle.utils import load_models,map_to_classes_names,sort_boxes_right_to_left,predict_image
#license_detection,char_detection_model=load_models('vehicle/models/license_detection.pt','vehicle/models/chars_detection.pt')
object_tracker=ObjectTracker(os.path.join('vehicle','models','tracker.pt'),[])
video_processor=VideoProcessor(object_tracker,[],print)
camera_list = []
cameras_object = []
def open_camera(request, id):
    camera = Cameras.objects.filter(id=id).first()
    return render(request, 'vehicle/detect_vehicle.html', context={
        "cameras": Cameras.objects.all(),
        "camera": camera,
    })
    

camera=None
@gzip.gzip_page
@require_GET
def verticle_camera(request, camera_id):
    global ids_vehicel, camera_list, cameras_object
    exists = False
    for obj in ids_vehicel:
        if obj['camera_id'] == camera_id:
            obj['labels'].clear()
            exists = True
            break
    
    if not exists:
        ids_vehicel.append({"camera_id": camera_id, "labels": []})
        
    cam = Cameras.objects.filter(id=camera_id).first()
    connection_string = cam.connection_string
    if connection_string == '0':
        connection_string = 0
    if connection_string == '1':
        connection_string = 1
    global camera
    if camera is not None:
        camera.stream.stop()
        camera=None
    camera = VideoStream(connection_string)
    camera.start()
    cameras.append({"id":cam.id, "camera": camera})
    return StreamingHttpResponse(generate(cam.id), content_type='multipart/x-mixed-replace; boundary=frame')

# def process_image_and_get_results(image, license_detection, char_detection_model):
#     list_plates = predict_image(image, license_detection)
#     for plate_image in list_plates:
#         results = char_detection_model.predict(plate_image, verbose=False)[0].cpu()
#         sorted_paird_boxes = sort_boxes_right_to_left(results.boxes.cls, results.boxes.xyxy, results.boxes.conf)
#         result = map_to_classes_names(sorted_paird_boxes[0])
def generate(camera_id):
    cap = cv2.VideoCapture('vehicle.mp4')
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        video_processor.process_frame(frame)
        # detect_vehicle(camera_id,frame,frame,'testtst')
        _, jpeg = cv2.imencode('.jpg', frame)
        
        #process_image_and_get_results(frame,license_detection,char_detection_model)

        data = jpeg.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
        