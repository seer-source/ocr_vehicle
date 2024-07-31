import torch
import os
from ultralytics import YOLO

names = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'ع', 11: 'أ', 12: 'ب', 13: 'س', 14: 'د', 15: 'ف',
         16: 'ج', 17: 'ه', 18: 'ق', 19: 'ل', 20: 'م', 21: 'ن', 22: 'ر', 23: 'ص', 24: 'س', 25: 'ت', 26: 'و', 27: 'ي', 28: 'ز'}

device=torch.device('cuda')  if torch.cuda.is_available() else torch.device('cpu') 

def sort_boxes_right_to_left(class_indices, bboxes, confidences):
    class_indices = class_indices.unsqueeze(1)
    confidences = confidences.unsqueeze(1)
    combined = torch.cat((class_indices, bboxes, confidences), dim=1)
    sorted_combined, indices = combined[:, 1:].sort(descending=True, dim=0)
    sorted_indices = indices[:, 0]
    sorted_class_indices = class_indices[sorted_indices].squeeze(1)
    sorted_bboxes = bboxes[sorted_indices]
    sorted_confidences = confidences[sorted_indices].squeeze(1)
    return sorted_class_indices, sorted_bboxes, sorted_confidences


def non_max_suppression(boxes, confidences, class_indices, iou_threshold=0.4):
    keep = []
    indices = torch.argsort(confidences, descending=True)
    while indices.numel() > 0:
        current = indices[0]
        keep.append(current)
        if indices.numel() == 1:
            break
        current_box = boxes[current].unsqueeze(0)
        remaining_boxes = boxes[indices[1:]]
        iou = bbox_iou(current_box, remaining_boxes)
        indices = indices[1:][iou <= iou_threshold]
    # Convert keep list to tensor of indices
    keep = torch.tensor(keep, dtype=torch.long)
    return boxes[keep], confidences[keep], class_indices[keep]


def bbox_iou(box1, box2):
    x1 = torch.max(box1[:, 0], box2[:, 0])
    y1 = torch.max(box1[:, 1], box2[:, 1])
    x2 = torch.min(box1[:, 2], box2[:, 2])
    y2 = torch.min(box1[:, 3], box2[:, 3])
    inter_area = (x2 - x1).clamp(0) * (y2 - y1).clamp(0)
    box1_area = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])
    box2_area = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area


license_detection = YOLO(os.path.join('vehicle','models', 'license_model.pt')).to(device)
char_detection_model = YOLO(os.path.join('vehicle','models', 'char_detection.pt')).to(device)


def map_to_classes_names(sorted_pair):
    text = []
    for id_cls in sorted_pair.tolist():
        if int(id_cls) in names:
            text.append(names[int(id_cls)])
    return text


def predict_image(frame):
    results = license_detection.predict(frame)[0].cpu()
    boxes = results.boxes.cpu().xyxy
    conf = results.boxes.conf
    list_of_images = []
    for box in boxes:
        x1, y1, x2, y2 = [round(i) for i in box.tolist()]
        list_of_images.append(results.orig_img[y1:y2, x1:x2])
    return list_of_images, conf


def process_image_and_get_results(main_frame,image):
    list_plates, confidence = predict_image(image)
    if len(list_plates)==2 or len(confidence)==2:
        temp_plate=None
        best_confidence=0
        for con,plate in zip(confidence,list_plates):
            if con>best_confidence:
                best_confidence=con
                temp_plate=plate
        confidence=best_confidence
        list_plates=[temp_plate]
        print('found two license')
    dict_of_results = {'license_confidence': confidence}
    for plate_image in list_plates:
        results = char_detection_model.predict(
            plate_image, save=True)[0].cpu()
        
        char_confidences = results.boxes.conf
        class_indices = results.boxes.cls
        bboxes = results.boxes.xyxy.cpu()
        # Apply Non-Maximum Suppression
        nms_boxes, nms_confidences, nms_class_indices = non_max_suppression(
            bboxes, char_confidences, class_indices)
        # Sort the results right to left
        sorted_pairs_boxes = sort_boxes_right_to_left(
            nms_class_indices, nms_boxes, nms_confidences)
        result = map_to_classes_names(sorted_pairs_boxes[0])
        dict_of_results['chars_confidence'] = sorted_pairs_boxes[2].tolist()
        dict_of_results['chars_result'] = result
        dict_of_results['license_plate']=plate_image
        dict_of_results['frame']=main_frame
    return dict_of_results





