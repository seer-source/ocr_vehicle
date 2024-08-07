import cv2
import numpy as np
from ultralytics import YOLO
import logging
from PIL import Image, ImageDraw, ImageFont
import io
import time
from .license_detection import process_image_and_get_results
import os

# Initialize logging
from app_resources.utils  import detect_vehicle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_single_license_result(result):
    # Extract license confidence
    license_confidence = result['license_confidence'].item()
    
    # Pair each character with its confidence score
    chars_with_confidences = list(zip(result['chars_result'], result['chars_confidence']))
    
    return chars_with_confidences

def get_highest_confidence_chars(predictions):
    # Process each prediction to get char-confidence pairs
    char_confidences_per_position = [process_single_license_result(pred) for pred in predictions]
    
    # Transpose the list to group confidences by character position
    transposed_confidences = list(zip(*char_confidences_per_position))
    
    # Get the highest confidence character for each position
    highest_confidence_chars = [
        max(position_confidences, key=lambda x: x[1]) for position_confidences in transposed_confidences
    ]
    
    return highest_confidence_chars

class Detections:
    def __init__(self, xyxy, mask, confidence, class_id, tracker_id, data):
        self.xyxy = xyxy
        self.mask = mask
        self.confidence = confidence
        self.class_id = class_id
        self.tracker_id = tracker_id
        self.data = data

def convert_detections_to_dict(detections_list):
    detections_dict = {
        'xyxy': [],
        'mask': [],
        'confidence': [],
        'class_id': [],
        'tracker_id': [],
        'data': []
    }

    for detection in detections_list:
        detections_dict['xyxy'].append(detection.xyxy)
        detections_dict['mask'].append(detection.mask)
        detections_dict['confidence'].append(detection.confidence)
        detections_dict['class_id'].append(detection.class_id)
        detections_dict['tracker_id'].append(detection.tracker_id)
        detections_dict['data'].append(detection.data)

    return detections_dict

def get_highest_confidence_license_plate(data):
    highest_confidence = -1
    best_license_plate = None
    frame = None
    
    for entry in data:
        confidence = entry['license_confidence'].item()  # Convert tensor to float
        if confidence > highest_confidence:
            highest_confidence = confidence
            best_license_plate = entry['license_plate']
            frame = entry['frame']
    
    return best_license_plate, frame

class TrackInfo:
    def __init__(self, track_id, initial_box, cls, confidence):
        self.track_id = track_id
        self.boxes = [initial_box]
        self.cls = cls
        self.status = None
        self.direction_determined = False
        self.max_confidence = confidence
        self.most_confident_class = cls
        self.initial_box = initial_box  # Store the initial box

    def update_box(self, new_box):
        self.boxes.append(new_box)
        if len(self.boxes) > 30:
            self.boxes.pop(0)

    def update_class(self, cls, confidence):
        if confidence > self.max_confidence:
            self.max_confidence = confidence
            self.most_confident_class = cls

    def determine_status(self, half_height, quarter_height):
        if len(self.boxes) < 15 or self.direction_determined:
            return

        start_box = self.boxes[0]
        end_box = self.boxes[-1]

        start_y = start_box[1]
        end_y = end_box[1]

        delta_y = end_y - start_y
        logging.info(f"Track {self.track_id} - start_y: {start_y}, end_y: {end_y}, delta_y: {delta_y}")

        if start_y < end_y and start_y < (half_height + quarter_height):
            self.status = "coming_on"
        elif start_y > end_y and start_y > (half_height - quarter_height):
            self.status = "going_off"

        self.direction_determined = True

class ObjectTracker:
    def __init__(self, model_path, polygon_points):
        self.model = YOLO(model_path)
        self.tracks = {}
        self.polygon_points = polygon_points
        self.valid_classes = ["car", "truck", "bus"]  # List of valid classes
        self.validated = set()  # Set to keep track of validated track IDs
        self.processed = set()  # Set to keep track of processed track IDs
        self.results_of_prediction = []

    def track(self, frame):
        return self.model.track(frame, persist=True)

    def check_confidence_to_store(self, track_id):
        if track_id in self.tracks:
            if len(self.tracks[track_id].boxes) >= 15:
                max_conf = self.tracks[track_id].max_confidence
                return max_conf > 0.60
            elif len(self.tracks[track_id].boxes) < 15:
                return True
            else:
                return False
        else:
            return True

    def update_tracks(self, boxes, track_ids, classes, confidences):
        for box, track_id, cls, confidence in zip(boxes, track_ids, classes, confidences):
            if cls in self.valid_classes and track_id not in self.processed:
                if self.check_confidence_to_store(track_id):
                    if track_id in self.tracks:
                        self.tracks[track_id].update_box(box)
                        self.tracks[track_id].update_class(cls, confidence)
                    else:
                        self.tracks[track_id] = TrackInfo(track_id, box, cls, confidence)

    def draw_tracks(self, frame, boxes):
        detections = []
        for track, box in zip(self.tracks.values(), boxes):
            x, y, w, h = box
            color = (0, 255, 0) if track.status == "coming_on" else (0, 0, 255)
            detection_label = f"{track.most_confident_class}: {track.status}"
            if track.status in ["coming_on", "going_off"]:
                detection = Detections(
                    xyxy=np.array([[int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + w / 2)]]),
                    confidence=np.array([1.0]),
                    class_id=np.array([['coming_on', 'going_off'].index(track.status)]),
                    tracker_id=track.track_id,
                    mask=None,
                    data=None
                )
                detections.append(detection)

        for detection in detections:
            x1, y1, x2, y2 = detection.xyxy[0]
            label = f"{['coming_on', 'going_off'][detection.class_id[0]]}: {detection.tracker_id}"
            color = (0, 255, 0) if "coming_on" in label else (255, 255, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame

    def clear_track_id(self, track_id):
        if track_id in self.tracks:
            del self.tracks[track_id]
            self.processed.add(track_id)

    def convert_to_absolute_points(self, relative_points, image_width, image_height):
        absolute_points = []
        for relative_x, relative_y in relative_points:
            x = int(relative_x * image_width)
            y = int(relative_y * image_height)
            absolute_points.append((x, y))
        return absolute_points

    def is_in_polygon(self, point, polygon):
        result = cv2.pointPolygonTest(np.array(polygon, dtype=np.int32), (int(point[0]), int(point[1])), False)
        return result >= 0

    def crop_object(self, frame, box):
        x, y, w, h = box
        x1 = max(0, int(x - w / 2))
        y1 = max(0, int(y - h / 2))
        x2 = min(frame.shape[1], int(x + w / 2))
        y2 = min(frame.shape[0], int(y + h / 2))
        return frame[y1:y2, x1:x2]

    def validate(self, trackId, main_frame, camera_id, image, callback):
        if len(self.results_of_prediction) >= 3:
            predictions = get_highest_confidence_chars(self.results_of_prediction)
            license_prediction = ' '.join([char for char, confidence in predictions])
            best_license_plate, frame = get_highest_confidence_license_plate(self.results_of_prediction)
            callback(trackId, camera_id, frame, cv2.cvtColor(best_license_plate, cv2.COLOR_BGR2RGB), license_prediction)
            self.results_of_prediction = []
            return True
        
        dict_of_results = process_image_and_get_results(main_frame, image)
        
        if len(dict_of_results['license_confidence'].flatten().tolist()) == 0:
            return False
        self.results_of_prediction.append(dict_of_results)
        return False

class VideoProcessor:
    def __init__(self, object_tracker, callback):
        self.object_tracker = object_tracker
        self.display_initialized = False
        self.callback = callback

    def process_frame(self, camera_id, frame):
        clean_frame = frame.copy()  # Create a clean copy of the frame for cropping
        height, width = frame.shape[:2]
        half_height = height / 2
        quarter_height = height / 4
        results = self.object_tracker.track(frame)
        if not results[0].boxes.is_track:
            return cv2.resize(frame, (640, 640))

        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        classes = [results[0].names[int(cls)] for cls in results[0].boxes.cls.cpu().tolist()]
        confidences = results[0].boxes.conf.cpu().tolist()
        self.object_tracker.update_tracks(boxes, track_ids, classes, confidences)
        for track in self.object_tracker.tracks.values():
            if not track.direction_determined:
                track.determine_status(half_height, quarter_height)
                logging.info(f"Track ID: {track.track_id}, Status: {track.status}, Class: {track.most_confident_class}")

        annotated_frame = self.object_tracker.draw_tracks(frame, boxes)
        track_ids_to_remove = []

        for track_id, track in list(self.object_tracker.tracks.items()):
            if track_id in self.object_tracker.validated:
                continue  # Skip already validated track IDs

            x, y, w, h = track.boxes[-1]
            front_edge_y = y + h / 2
            rear_edge_y = y - h / 2

            # Visualize front and rear edges
            cv2.circle(frame, (int(x), int(front_edge_y)), 5, (255, 0, 0), -1)  # Blue for front edge
            cv2.circle(frame, (int(x), int(rear_edge_y)), 5, (0, 0, 255), -1)  # Red for rear edge

            if track.status == "coming_on":
                if front_edge_y > half_height + quarter_height:
                    if track.track_id not in self.object_tracker.validated:
                        cropped_object = self.object_tracker.crop_object(clean_frame, track.boxes[-1])
                        if self.object_tracker.validate(track.track_id, clean_frame, track.status, cropped_object, self.callback):
                            self.object_tracker.validated.add(track.track_id)
                            track_ids_to_remove.append(track.track_id)
            elif track.status == "going_off":
                if front_edge_y < half_height + quarter_height:
                    if track.track_id not in self.object_tracker.validated:
                        cropped_object = self.object_tracker.crop_object(clean_frame, track.boxes[-1])
                        if self.object_tracker.validate(track.track_id, clean_frame, track.status, cropped_object, self.callback):
                            self.object_tracker.validated.add(track.track_id)
                            track_ids_to_remove.append(track.track_id)
                            
        for track_id in track_ids_to_remove:
            self.object_tracker.clear_track_id(track_id)

        return cv2.resize(annotated_frame, (620, 620))

tracker = ObjectTracker(os.path.join('vehicle','models', 'object_tracker.pt'), [])

# import os
# from uuid import uuid1

# def save_tracks(trackId, camera_id, frame, license_img, chars):
#     os.makedirs('stored', exist_ok=True)
#     image_id = str(uuid1())
#     cv2.imwrite(f"stored/{camera_id}___{trackId}__frame_{image_id}_.jpg", frame)
#     cv2.imwrite(f"stored/{camera_id}__{trackId}__license_img_{chars}__{image_id}_.jpg", license_img)

video_process = VideoProcessor(tracker,detect_vehicle)

# import cv2 as cv

# cap = cv.VideoCapture('vehicle/Cars All.mp4')
# if not cap.isOpened():
#     print("Error: Could not open video file.")
# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         print("Reached end of video or there is an issue with the video file.")
#         break
#     frame = video_process.process_frame('camera_id one', frame)
#     cv.imshow('Video Frame', frame)
#     if cv.waitKey(25) & 0xFF == ord('q'):
#         break

# cap.release()
# cv.destroyAllWindows()
