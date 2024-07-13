
from ultralytics import YOLO
import numpy as np
import torch
import time
import cv2      
classes={
 0: 'أ',
 1: 'ب',
 2: 'د',
 3: '٨',
 4: 'ع',
 5: 'ف',
 6: '٥',
 7: '٤',
 8: 'ج',
 9: 'ه',
 10: 'ك',
 11: 'ل',
 12: 'م',
 13: '٩',
 14: 'ن',
 15: '١',
 16: 'ق',
 17: 'ر',
 18: 'ص',
 19: 'س',
 20: '٧',
 21: '٦',
 22: 'ط',
 23: '٣',
 24: '٢',
 25: 'و',
 26: 'ي'
}

def map_to_classes_names(classes_indexes):
    classes_indexes=classes_indexes.tolist()
    return ' '.join([classes[i] for i in classes_indexes])
def load_models(license_detection_model_path,char_detection_model_path,verbose=True):
    # Load the license plate detection model
    license_detection = YOLO(license_detection_model_path)
    
    # Load the character detection model
    char_detection_model = YOLO(char_detection_model_path)
    
    return license_detection, char_detection_model
def elapsed_time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        #print(f"Elapsed time: {elapsed_time:.2f} in fun name {func.__name__} seconds")
        return result
    return wrapper
@elapsed_time_decorator
def process_image(frame):
    #checking the type of frame if it is not numpy array then convert it to numpy array
    if not isinstance(frame, np.ndarray):     
        frame = np.array(frame)
    #checking the type of string read it as image
    if isinstance(frame, str):
        frame = cv2.imread(frame)
    #frame=remove_noise(frame)
    #frame=correct_brightness(frame)
    #frame=enhance_resolution(frame)
    frame=correct_skew(frame)
    return frame
def ocr_license_plate(frame,license_detection,char_detection_model):
    list_of_plate_results=[]
    license_plates=predict_image(frame,license_detection)
    for plate_image in license_plates:
        plate_image=process_image(plate_image)
        results=char_detection_model.predict(plate_image,verbose=False)[0].cuda()
        classes_indexes,bboxes,conf=sort_boxes_right_to_left(results.boxes.cls,results.boxes.xyxy,results.boxes.conf)
        list_of_plate_results.append({'cls':classes_indexes,'xyxy':bboxes,'conf':conf,'img':plate_image})
    return list_of_plate_results


def remove_noise(image, method='gaussian', kernel_size=5):
    if method == 'gaussian':
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    elif method == 'bilateral':
        return cv2.bilateralFilter(image, kernel_size, 75, 75)
    else:
        raise ValueError("Method should be 'gaussian' or 'bilateral'")

def correct_brightness(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)

def enhance_resolution(image, scale_factor=2.0):
    height, width = image.shape[:2]
    return cv2.resize(image, (int(width * scale_factor), int(height * scale_factor)), interpolation=cv2.INTER_CUBIC)

# Function to call all the individual enhancements
def enhance_image(image, noise_method='gaussian', kernel_size=5, clip_limit=2.0, tile_grid_size=(8, 8), scale_factor=2.0):
    noise_reduced_img = remove_noise(image, method=noise_method, kernel_size=kernel_size)
    brightness_corrected_img = correct_brightness(noise_reduced_img, clip_limit=clip_limit, tile_grid_size=tile_grid_size)
    enhanced_resolution_img = enhance_resolution(brightness_corrected_img, scale_factor=scale_factor)
    return enhanced_resolution_img
@elapsed_time_decorator
def predict_image(frame,license_detection):
    results=license_detection.predict(frame,verbose=False)[0].cpu()
    boxes=results.boxes.xyxy
    list_of_license_plates=[]
    for box in boxes:
        x1,y1,x2,y2=[round(i) for i in box.tolist()]
        list_of_license_plates.append(results.orig_img[y1:y2,x1:x2])
    return list_of_license_plates

def correct_skew(image, delta=1, limit=5):
    """
    Correct image skew by finding the main text orientation angle and rotating the image accordingly.
    
    :param image: Input image
    :param delta: Angle precision during lines detection
    :param limit: Maximum allowed skew angle to correct
    :return: Skew-corrected image
    """
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use edge detection to find lines in the image
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect lines in the image using HoughLinesP
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    
    # Calculate the angle for each detected line
    angles = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)
    
    # Calculate the median angle of all the lines
    median_angle = np.median(angles)
    
    # If the angle is large (which is unlikely for text), then don't correct the skew
    if -limit < median_angle < limit:
        # Rotate the image by the median angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        corrected_img = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    else:
        corrected_img = image
    
    return corrected_img
@elapsed_time_decorator
def sort_boxes_right_to_left(class_indices, bboxes, conf):
    # Ensure class_indices is a column vector
    class_indices = class_indices.unsqueeze(1)

    # Combine the class indices, bounding boxes, and conf into a single tensor
    combined = torch.cat((class_indices, bboxes, conf.unsqueeze(1)), dim=1)

    # Sort by x1 values (second column) in descending order
    sorted_combined, indices = combined[:, 1].sort(descending=True, dim=0)

    # Extract the sorted indices for class_indices
    sorted_indices = indices

    # Use the sorted indices to reorder class_indices, bboxes, and conf
    sorted_class_indices = class_indices[sorted_indices].squeeze(1)
    sorted_bboxes = bboxes[sorted_indices]
    sorted_conf = conf[sorted_indices]

    # Return the sorted class_indices, bounding boxes, and conf
    return sorted_class_indices, sorted_bboxes, sorted_conf




