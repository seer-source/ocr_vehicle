import cv2
import numpy as np
import torch

from detect import detect
from models.experimental import attempt_load
from src.char_classification.model import CNN_Model
from utils_LP import character_recog_CNN, crop_n_rotate_LP
import sys

Min_char = 0.01
Max_char = 0.09
image_path = './Capture.PNG'
CHAR_CLASSIFICATION_WEIGHTS = './weight.h5'
LP_weights = './LP_detect_yolov7_500img.pt'

model_char = CNN_Model(trainable=False).model
model_char.load_weights(CHAR_CLASSIFICATION_WEIGHTS)



if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

model_LP = attempt_load(LP_weights, map_location=device)

source_img = cv2.imread(image_path)
pred, LP_detected_img,result = detect(model_LP, source_img, device, imgsz=640)

