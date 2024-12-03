#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
from pycocotools.coco import COCO
import os
import json
import re
import argparse
import torch
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image
from torchvision.transforms import functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from PIL import Image
coco_category_mapping = {
    "person": "人",
    "bicycle": "自行车",
    "car": "汽车",
    "motorcycle": "摩托车",
    "airplane": "飞机",
    "bus": "公共汽车",
    "train": "火车",
    "truck": "卡车",
    "boat": "船",
    "traffic light": "红绿灯",
    "fire hydrant": "消防栓",
    "stop sign": "停止标志",
    "parking meter": "停车收费表",
    "bench": "长椅",
    "bird": "鸟",
    "cat": "猫",
    "dog": "狗",
    "horse": "马",
    "sheep": "羊",
    "cow": "牛",
    "elephant": "大象",
    "bear": "熊",
    "zebra": "斑马",
    "giraffe": "长颈鹿",
    "backpack": "背包",
    "umbrella": "雨伞",
    "handbag": "手提包",
    "tie": "领带",
    "suitcase": "行李箱",
    "frisbee": "飞盘",
    "skis": "滑雪板",
    "snowboard": "单板滑雪",
    "sports ball": "球",
    "kite": "风筝",
    "baseball bat": "棒球棒",
    "baseball glove": "棒球手套",
    "skateboard": "滑板",
    "surfboard": "冲浪板",
    "tennis racket": "网球拍",
    "bottle": "瓶子",
    "wine glass": "酒杯",
    "cup": "杯子",
    "fork": "叉子",
    "knife": "刀",
    "spoon": "勺子",
    "bowl": "碗",
    "banana": "香蕉",
    "apple": "苹果",
    "sandwich": "三明治",
    "orange": "橙子",
    "broccoli": "西兰花",
    "carrot": "胡萝卜",
    "hot dog": "热狗",
    "pizza": "比萨",
    "donut": "甜甜圈",
    "cake": "蛋糕",
    "chair": "椅子",
    "couch": "沙发",
    "potted plant": "盆栽植物",
    "bed": "床",
    "dining table": "餐桌",
    "toilet": "厕所",
    "tv": "电视",
    "laptop": "笔记本电脑",
    "mouse": "鼠标",
    "remote": "遥控器",
    "keyboard": "键盘",
    "cell phone": "手机",
    "microwave": "微波炉",
    "oven": "烤箱",
    "toaster": "烤面包机",
    "sink": "水槽",
    "refrigerator": "冰箱",
    "book": "书",
    "clock": "时钟",
    "vase": "花瓶",
    "scissors": "剪刀",
    "teddy bear": "泰迪熊",
    "hair drier": "吹风机",
    "toothbrush": "牙刷"
}

def translate_category(category_name, mapping_dict):
    """
    Translate the category name to Chinese using the provided mapping dictionary.

    :param category_name: str, the category name in English.
    :param mapping_dict: dict, the mapping dictionary from English to Chinese.
    :return: str, the translated category name in Chinese.
    """
    return mapping_dict.get(category_name, category_name)

def resize_image_and_bbox(image_path, bbox, target_width=720, target_height=1280):
    image = Image.open(image_path).convert('RGB')
    orig_width, orig_height = image.size

    # Resize the image
    image = F.resize(image, (target_height, target_width))

    # Calculate the scaling factors
    scale_x = target_width / orig_width
    scale_y = target_height / orig_height

    # Scale the bounding box coordinates
    x1, y1, width, height = bbox
    x2 = x1 + width
    y2 = y1 + height

    x1_new = int(x1 * scale_x)
    y1_new = int(y1 * scale_y)
    x2_new = int(x2 * scale_x)
    y2_new = int(y2 * scale_y)

    return image, x1_new, y1_new, x2_new, y2_new

def calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, x1_target, y1_target, x2_target, y2_target):
    x1_inter = max(x1_pred, x1_target)
    y1_inter = max(y1_pred, y1_target)
    x2_inter = min(x2_pred, x2_target)
    y2_inter = min(y2_pred, y2_target)

    inter_width = max(0, x2_inter - x1_inter)
    inter_height = max(0, y2_inter - y1_inter)

    inter_area = inter_width * inter_height
    pred_area = (x2_pred - x1_pred) * (y2_pred - y1_pred)
    target_area = (x2_target - x1_target) * (y2_target - y1_target)
    union_area = pred_area + target_area - inter_area
    iou = inter_area / union_area if union_area != 0 else 0

    return iou

def get_parser():
    parser = argparse.ArgumentParser(description="Agent for mobile phone")
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
    parser.add_argument('--model', type=str, default='checkpoint518-2600', help='model to use')
    parser.add_argument('--dataset', type=str, default='/home/corpus/test_515/test_data/seen_data/ref_test', help='dataset to use')
    parser.add_argument('--output_dir', type=str, default='/home/corpus/test_515/result/seen_coco_ckpt518_2600.json', help='dataset to use')
    parser.add_argument('--coco_ann_file', type=str, default='/home/corpus/dataset/coco2017/annotations/instances_val2017.json', help='COCO annotation file')
    parser.add_argument('--coco_image_dir', type=str, default='/home/corpus/dataset/coco2017/val2017', help='COCO image directory')
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    torch.manual_seed(1234)
    
    # 加载 COCO 数据集
    coco = COCO(args.coco_ann_file)
    
    if args.model == "checkpoint518-2600":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-2600"
    elif args.model == "qwen-vl":
        model_path = "/home/corpus/ckpt/Qwen-VL-Chat"
    elif args.model == "checkpoint518-3800":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-3800"
    
    # Ensure that the directory contains necessary files
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The specified model path {model_path} does not exist.")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)
    # Use CUDA device for model
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cuda", trust_remote_code=True, local_files_only=True).eval()
    # Specify hyperparameters for generation
    model.generation_config = GenerationConfig.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)

    output_path = args.output_dir
    all_data = []
    total = 0
    
    # 遍历 COCO 数据集的图像和注释
    img_ids = coco.getImgIds()
    n = 0 
    for img_id in tqdm(img_ids, desc="Processing COCO images"):
        img_info = coco.loadImgs(img_id)[0]
        img_width, img_height = img_info['width'], img_info['height']
        # print(img_width, img_height)
        ann_ids = coco.getAnnIds(imgIds=img_id, iscrowd=False)
        anns = coco.loadAnns(ann_ids)
        
        current_image_path = os.path.join(args.coco_image_dir, img_info['file_name'])
        
        
        
        category_counts = {}
        for ann in anns:
            category_id = ann['category_id']
            category = coco.loadCats(category_id)[0]['name']
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
        
        # 仅处理出现次数为1的类别
        for ann in anns:
            category_id = ann['category_id']
            category = coco.loadCats(category_id)[0]['name']
            
            # 如果该类别在anns中出现多次，跳过
            if category_counts[category] > 1:
                continue
            bbox = ann['bbox']
            image_resized, x1_target, y1_target, x2_target, y2_target = resize_image_and_bbox(current_image_path, bbox, 720, 1280)
            temp_image_path = os.path.join(args.coco_image_dir, "resized_image.png")
            print(current_image_path)
            image_resized.save(temp_image_path)
            print(x1_target, y1_target, x2_target, y2_target)
            # 由原图尺寸映射到 720*1280 尺寸上。
            translated_name = translate_category(category, coco_category_mapping)
            query = tokenizer.from_list_format([
                {'image': temp_image_path},
                {'text': f'如何定位到界面中的\"{translated_name}\"。'}
            ])
            
            response, history = model.chat(tokenizer, query=query, history=None)
            print(response)

            # max_iou = 0
            match1 = re.search(r'\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\]', response)
            if match1:
                bounds1 = [match1.group(1), match1.group(2)]
                x1_pred, y1_pred = map(int, bounds1[0].split(','))
                x2_pred, y2_pred = map(int, bounds1[1].split(','))
                result = calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, x1_target, y1_target, x2_target, y2_target)
            else:
                result = 0
                print("未匹配成功！")
                
            total += result
            n += 1
            acc = total / n
            print("[IOU]:", result)
            print("[average IOU]:", acc)
            data = {
                "image_id": img_id,
                "predict_box": response,
                "target_box": f"[{x1_target}, {y1_target}][{x2_target}, {y2_target}]",
                "iou": result,
                "average_iou": acc
            }
            all_data.append(data)
    
    with open(output_path, "w", encoding='UTF-8') as fp:
        json.dump(all_data, fp, ensure_ascii=False, indent=4)
