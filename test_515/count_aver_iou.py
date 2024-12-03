#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.      
import re
import json

def extract_coordinates(box_str):
    # 提取四个数字
    numbers = re.findall(r'\d+', box_str)
    if len(numbers) == 4:
        return list(map(int, numbers))
    return None

def scale_coordinates(coords, width, height, target_width, target_height):
    x1, y1, x2, y2 = coords
    x1 = int(x1 * target_width / width)
    y1 = int(y1 * target_height / height)
    x2 = int(x2 * target_width / width)
    y2 = int(y2 * target_height / height)
    return [x1, y1, x2, y2]

def calculate_iou(box1, box2):
    x1, y1, x2, y2 = box1
    tx1, ty1, tx2, ty2 = box2

    xi1 = max(x1, tx1)
    yi1 = max(y1, ty1)
    xi2 = min(x2, tx2)
    yi2 = min(y2, ty2)

    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (tx2 - tx1) * (ty2 - ty1)

    union_area = box1_area + box2_area - inter_area

    iou = inter_area / union_area if union_area != 0 else 0
    return iou

json_file_path = '/home/corpus/test_515/result/grounding/seen_ref_qwenplus.json'

with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

total_iou = 0
count = 0

# 处理每个数据项
for item in data:
    predict_box_str = item["predict box"]
    target_box_str = item["target box"]

    # 提取预测框和目标框坐标
    predict_coords = extract_coordinates(predict_box_str)
    target_coords = extract_coordinates(target_box_str)

    if predict_coords and target_coords:
        # 缩放预测框坐标
        scaled_predict_coords = scale_coordinates(predict_coords, 1000, 1000, 720, 1280)

        # 提取目标框的数字并转化为坐标
        target_coords = [int(num) for num in re.findall(r'\d+', target_box_str)]

        # 计算IOU
        iou = calculate_iou(scaled_predict_coords, target_coords)
        print(f"IOU for {item['subpath']}: {iou}")
        total_iou += iou
        count += 1
    else:
        print(f"Failed to extract coordinates for {item['subpath']}")

average_iou = total_iou / count if count > 0 else 0
print(f"Average IOU: {average_iou}")
