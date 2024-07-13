import time

import cv2
import torch
from numpy import random

from models.experimental import attempt_load
from utils.datasets import transform_img
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import time_synchronized
import pandas as pd
#from img2text import Img2text
import os
import numpy as np
import easyocr


# Initialize the OCR network
#ocr_network = Img2text(unicharset_path="ocr_models/Azka.unicharset", weights_path="ocr_models/Azka_199_7.679617075813962.weights")
def detect(model, image, device, imgsz=1024, conf_thres=0.25,
           iou_thres=0.45, augment=False, classes=0, agnostic_nms=False):
    '''
    Find license Plate with YOLOv7
    :return:

    Pred:
        coordinates of LP
    im0:
        original image with LP plot
    '''
    # Initialize


    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    # model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size

    #model.half()  # to FP16

    # Transform image to predict
    img, im0 = transform_img(image)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference

    t0 = time.time()
    img = torch.from_numpy(img).to(device)#torch.from_numpy(img).to(device).half() if half else torch.from_numpy(img).to(device).float()

#
    img = img.half() if half else img.float() #img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    t1 = time_synchronized()
    pred = model(img, augment=augment)[0]
    t2 = time_synchronized()
    # Apply NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms)
    t3 = time_synchronized()
    final_pred = []

    for i, det in enumerate(pred):  # detections per image
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            final_pred.append(det)
            # Write results
            for *xyxy, conf, cls in reversed(det):
                label = f'{names[int(cls)]} {conf:.2f}'
                plat_image = plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=1)
                reader = easyocr.Reader(['ar'])
                result =reader.readtext(plat_image ,paragraph = True,text_threshold =0.15,low_text=0.2,add_margin=0.09) #reader.readtext(plat_image)#reader.readtext(img ,paragraph = True,text_threshold =0.15,low_text=0.2,add_margin=0.09)
                #result_text = ocr_network.detect_text(["Hyper one_0bc04ea4-6c55-498d-acf1-bd6690a0c25a_item.jpg"])
                #print(result[0][1])
                if len(result>=0):
                    numberofcar=result[0][1]
                else:
                    numberofcar=""    

                #cv2.imwrite('annotated_image333.jpg', plat_image)


        # Print time (inference + NMS)
        #print(f'Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS')
        #print('Number of License Plate:', len(det))

        # cv2.imshow('Detected license plates', cv2.resize(im0, dsize=None, fx=0.5, fy=0.5))

#print(f'Done. ({time.time() - t0:.3f}s)')
    return final_pred[0].to(device='cpu').detach().numpy(), im0 ,numberofcar
def detect_video(model, image, device, imgsz=1024, conf_thres=0.25,
           iou_thres=0.45, augment=False, classes=0, agnostic_nms=False):
    '''
    Find license Plate with YOLOv7
    :return:

    Pred:
        coordinates of LP
    im0:
        original image with LP plot
    '''
    # Initialize
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model and stride
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size

    # Transform image to predict
    img, im0 = transform_img(image)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    t0 = time.time()
    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # normalize to 0.0 - 1.0 range
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    t1 = time_synchronized()
    pred = model(img, augment=augment)[0]
    t2 = time_synchronized()
    # Apply NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms)
    t3 = time_synchronized()
    final_pred = []

    for i, det in enumerate(pred):  # detections per image
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            final_pred.append(det)
            # Write results
            for *xyxy, conf, cls in reversed(det):
                label = f'{names[int(cls)]} {conf:.2f}'
                plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=1)
                # OCR and other processing can go here

    # Check if final_pred is not empty before accessing
    if len(final_pred) > 0:
        processed_pred = final_pred[0].to(device='cpu').detach().numpy()
    else:
        print("No license plates detected")
        processed_pred = None

    print(f'Done. ({time.time() - t0:.3f}s)')
    return processed_pred, im0


def main():
    weights = './LP_detect_yolov7_500img.pt'
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    model = attempt_load(weights, map_location=device)
    image_path = './1-s2.0-S1110016813000276-gr2.jpg'
    source_img = cv2.imread(image_path)
    #cv2.imshow('input', cv2.resize(source_img, dsize=None, fx=0.5, fy=0.5))
    final_pred = detect(model, source_img,device, imgsz=640)
    """output_image_path = './output_image.jpg'
    final_pred_np = np.array(final_pred)
    cv2.imwrite(output_image_path, final_pred_np)"""
     # Extract the annotated image from final_pred
    """annotated_image = final_pred[1]
    
    # Save the annotated image
    output_image_path = './output_image.jpg'
    cv2.imwrite(output_image_path, annotated_image)"""

    """if final_pred:
        det = final_pred
        for *xyxy, conf, cls in reversed(det):
            x = xyxy
            print(x)
            x_min, y_min, x_max, y_max = int(x[0]), int(x[1]), int(x[2]), int(x[3])
            print(x_min, y_min, x_max, y_max)
            # Extract the region of interest
            roi = source_img[y_min:y_max, x_min:x_max]

            # Save the detected license plate region
            cv2.imwrite('detected_license_plate.jpg', roi)

            #cv2.imshow('output', cv2.resize(roi, dsize=None, fx=1, fy=1))
            #cv2.waitKey(0)"""
    
    #print('final_pred', final_pred)

    #cv2.imshow('output', cv2.resize(source_img, dsize=None, fx=1, fy=1))
    #cv2.waitKey(0)


if __name__ == '__main__':
    main()
