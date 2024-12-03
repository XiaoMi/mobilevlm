#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
from transformers.generation import GenerationConfig
import torch
import re
import os
from tqdm import tqdm
import json
import argparse
from test_515_prompt import *
from gpt import *
from sklearn.metrics import f1_score
import torchvision.transforms as T
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
# from data.template.template_cn_multi import *
import dashscope
from dashscope import MultiModalConversation
dashscope.api_key=""
w = 720
h = 1280 
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
def build_transform(input_size):
    MEAN, STD = IMAGENET_MEAN, IMAGENET_STD
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=MEAN, std=STD)
    ])
    return transform

def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    best_ratio_diff = float('inf')
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio
def dynamic_preprocess(image, min_num=1, max_num=6, image_size=448, use_thumbnail=False):
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in range(1, n + 1) if
        i * j <= max_num and i * j >= min_num)
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images


def load_image(image_file, input_size=448, max_num=6):
    image = Image.open(image_file).convert('RGB')
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(image, image_size=input_size, use_thumbnail=True, max_num=max_num)
    pixel_values = [transform(image) for image in images]
    pixel_values = torch.stack(pixel_values)
    return pixel_values

def calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, target_box):
    match2 = re.search(r'\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\]', target_box)
    if match2:
        bounds2 = [match2.group(1), match2.group(2)]
        # 解析bounds字符串"[x1,y1][x2,y2]"
        x1_target, y1_target = map(int, bounds2[0].split(','))
        x2_target, y2_target = map(int, bounds2[1].split(','))
    else:
        return 0
        # 计算交集区域的坐标
    x1_inter = max(x1_pred, x1_target)
    y1_inter = max(y1_pred, y1_target)
    x2_inter = min(x2_pred, x2_target)
    y2_inter = min(y2_pred, y2_target)

    # 计算交集区域的宽度和高度
    inter_width = max(0, x2_inter - x1_inter)
    inter_height = max(0, y2_inter - y1_inter)

    # 计算交集区域的面积
    inter_area = inter_width * inter_height

    # 计算每个框的面积
    pred_area = (x2_pred - x1_pred) * (y2_pred - y1_pred)
    target_area = (x2_target - x1_target) * (y2_target - y1_target)

    # 计算并集区域的面积
    union_area = pred_area + target_area - inter_area

    # 计算交并比
    iou = inter_area / union_area if union_area != 0 else 0

    return iou

def calculate_acc(predict, target):  # 做文本准确度计算
    if "click" in predict and "click" in target:
        match = re.search(r'<ref>([^,]+)</ref>', predict)
        if match:
            text_match = match.group(1)
            if text_match in target:
                return 1
            else:
                return 0
        else:
            return 0 
    if "input" in predict and "input" in target:
        match = re.search(r'<ref>([^,]+)</ref>', predict)
        if match:
            text_match = match.group(1)
            if text_match in target:
                return 1
            else:
                return 0
        else:
            return 0
    if "scroll" in predict and "scroll" in target:
        match1 = re.search(r'\],([^,]+)\)', predict)
        match2 = re.search(r'\],([^,]+)\)', target)
        if match1 and match2:
            direction1 = match1.group(1)
            direction2 = match2.group(1)
            if direction1 == direction2:
                return 1 
            else:
                return 0
        else:
            return 0
    else:
        return 0

def calculate_ocr(predict, target):  # 做文本准确度计算
    if "click" in target:
        match = re.search(r'<ref>([^,]+)</ref>', target)
        if match:
            text_match = match.group(1)
            # print("target:", text_match)
            if text_match in predict:
                return 1
            else:
                return 0
        else:
            return 0 
    if "input" in target:
        match = re.search(r'<ref>([^,]+)</ref>', target)
        if match:
            text_match = match.group(1)
            if text_match in predict:
                return 1
            else:
                return 0
        else:
            return 0
    if "scroll" in target:
        match1 = re.search(r'\],([^,]+)\)', predict)
        match2 = re.search(r'\],([^,]+)\)', target)
        if match1 and match2:
            direction1 = match1.group(1)
            direction2 = match2.group(1)
            if direction1 == direction2:
                return 1 
            else:
                return 0
        else:
            return 0
    else:
        return 0




def get_parser():
    parser = argparse.ArgumentParser(description="Agent for mobile phone")
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
    parser.add_argument('--model', type=str, default='qwen-vl-max', help='model to use')
    parser.add_argument('--dataset', type=str, default='/home/corpus/test_515/test_data/seen_data/navigation_test', help='dataset to use')
    parser.add_argument('--output_dir', type=str, default='/home/corpus/test_515/result/navigation/seen_navigation_stage2-qwenmax.json', help='dataset to use')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    torch.manual_seed(1234)
    model_path = None
    if args.model == "checkpoint514":
        model_path = "/home/corpus/ckpt/qwen_stage2_1task_0514/checkpoint-6000"
    elif args.model == "qwen-vl":
        model_path = "/home/corpus/ckpt/Qwen-VL-Chat"
    elif args.model == "checkpoint524-4200":
        model_path = "/home/corpus/ckpt/qwen_stage2_1task_0524-backup/checkpoint-4200"
    elif args.model == "checkpoint524-1700":
        model_path = "/home/corpus/ckpt/qwen_stage2_1task_0524-backup/checkpoint-1700"
    elif args.model == "stage3-ckpt1000":
        model_path = "/home/corpus/ckpt/qwen_stage3_ScreenSelf_0511/checkpoint-1000"
    elif args.model == "Internvl":
        model_path = '/home/corpus/open_source_model/InternVL'
    elif args.model == "chinesellava":
        model_path = "/home/corpus/open_source_model/Chinses-LLaVA"
        
    if model_path is not None:    
        # Ensure that the directory contains necessary files
        if model_path != "/home/corpus/open_source_model/InternVL":
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)
            # Use CUDA device for model
            model = AutoModelForCausalLM.from_pretrained(model_path, device_map="cuda", trust_remote_code=True, local_files_only=True).eval()
            # Specify hyperparameters for generation
            model.generation_config = GenerationConfig.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)
        elif model_path == "/home/corpus/open_source_model/InternVL":
            model = AutoModel.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            trust_remote_code=True).eval().cuda()
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            generation_config = dict(
            num_beams=1,
            max_new_tokens=512,
            do_sample=False,
            )
    root_dir = args.dataset
    output_path = args.output_dir
    all_data = []
    total = 0
    iou_total = 0
    subdirs = [subdir for subdir in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, subdir))]
    n = 0 
    for subdir in tqdm(subdirs, desc="Processing subdirectories"):
        subdir_path = os.path.join(root_dir, subdir)
        # print(subdir_path)
        if os.path.isdir(subdir_path):
            current_input_filename = f"{subdir}-input.txt"
            current_output_filename = f"{subdir}-output.txt"
            current_image_filename = f"{subdir}-screen.png"
            parent_prefix = '_'.join(subdir.split('_')[:-1])
            parent_image_filename = f"{parent_prefix}-screen.png"
            current_input_path = os.path.join(subdir_path, current_input_filename)
            current_output_path = os.path.join(subdir_path, current_output_filename)
            current_image_path = os.path.join(subdir_path, current_image_filename)
            parent_image_path = os.path.join(subdir_path, parent_image_filename)
            if os.path.exists(current_image_path):
                with open(current_input_path, 'r', encoding='utf-8') as file:
                    input = file.read()
                with open(current_output_path, 'r', encoding='utf-8') as file:
                    output = file.read()
                if args.model.startswith("checkpoint524") or args.model.startswith("stage3"):
                    query = tokenizer.from_list_format([
                    {'text':"第一张图片："},
                    {'image': parent_image_path}, # Either a local path or an url
                    {'text':"第二张图片："},
                    {'image': current_image_path}, # Either a local path or an url
                    {'text': input},
                                        ])
                    response, history = model.chat(tokenizer, query=query, history=None)

                elif args.model == "qwen-vl":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    input = navigation_qwen_prompt
                    query = tokenizer.from_list_format([
                        {'text': input},
                        {'text':"问：第一张图片："},
                        {'image': parent_image_path}, # Either a local path or an url
                        {'text':"第二张图片："},
                        {'image': current_image_path}, # Either a local path or an url
                        {'text': f"{question}\n 答："},
                                        ])
                    # query = tokenizer.from_list_format([
                    #     {'text': input},
                    #     {'text':"问：给定两个手机截图，告诉我应该和什么控件进行一次交互可以从第一张图片到第二张图片，交互动作有三种动作：点击、输入、滑动。请以\"动作 值 位置\"回答。图片一："},
                    #     {'image': parent_image_path}, # Either a local path or an url
                    #     {'text':"图片二："},
                    #     {'image': current_image_path}, # Either a local path or an url
                    #     {'text': f"如何从第一张图导航到第二张图？\n 答："},
                    #                     ])
                    response, history = model.chat(tokenizer, query=query, history=None)
                
                elif args.model == "gpt-4v":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    text1 = '这个界面的哪个控件可导航至第二张图片？'
                    ans1 = 'click(<ref>周四</ref><box>[563,163][603,185]</box>)'
                    image_path1 = '/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018-screen.png'
                    image_path2 = '/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018_13545-screen.png'
                    text2 = '哪个控件可以直接到第二张图片？'
                    ans2 = 'click(<ref>直播</ref><box>[200,1132][240,1160]</box>)'
                    image_path3 = '/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29-screen.png'
                    image_path4 = '/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29_29-screen.png'
                    input = f"{question}"
                    response = gpt_4v_navigation(text1, image_path1, image_path2, ans1, text2, image_path3, image_path4, ans2, question, parent_image_path, current_image_path)
                    response = response['response']
                
                elif args.model == "qwen-vl-plus":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    text1 = '这个界面的哪个控件可导航至第二张图片？'
                    ans1 = 'click(<ref>周四</ref><box>[563,163][603,185]</box>)'
                    image_path1 = '/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018-screen.png'
                    image_path2 = '/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018_13545-screen.png'
                    text2 = '哪个控件可以直接到第二张图片？'
                    ans2 = 'click(<ref>直播</ref><box>[200,1132][240,1160]</box>)'
                    image_path3 = '/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29-screen.png'
                    image_path4 = '/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29_29-screen.png'
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"image": image_path3},
                                {"image": image_path4},
                                {"text1": text2}
                            ]
                        },
                        {
                            "role": "assistant",
                            "content": [
                                {"text1": ans2}
                            ]
                        },
                        {
                            "role": "user",
                            "content": [
                                {"image": parent_image_path},
                                {"image": current_image_path},
                                {"text": f"{question}, click(<ref>0.00</ref><box>[612,700][674,738]</box>) "}
                            ]
                        },
                    ]
                    response = dashscope.MultiModalConversation.call(model='qwen-vl-plus',
                                                     messages=messages)
                    print(response)
                    try:
                        response = response['output']['choices'][0]['message']['content'][0]['text']
                    except (KeyError, TypeError, IndexError):
                        response = ""
                elif args.model == "qwen-vl-max":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    text1 = '这个界面的哪个控件可导航至第二张图片？'
                    ans1 = 'click(<ref>周四</ref><box>[563,163][603,185]</box>)'
                    image_path1 = '/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018-screen.png'
                    image_path2 = '/home/corpus/test_515/few_shot/navigation/ctrip0_1_36_313_3617_1988_3587_3018_13545/ctrip0_1_36_313_3617_1988_3587_3018_13545-screen.png'
                    text2 = '哪个控件可以直接到第二张图片？'
                    ans2 = 'click(<ref>直播</ref><box>[200,1132][240,1160]</box>)'
                    image_path3 = '/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29-screen.png'
                    image_path4 = '/home/corpus/test_515/few_shot/navigation/QQmusic0_29_29/QQmusic0_29_29-screen.png'
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"image": image_path3},
                                {"image": image_path4},
                                {"text1": text2}
                            ]
                        },
                        {
                            "role": "assistant",
                            "content": [
                                {"text1": ans2}
                            ]
                        },
                        {
                            "role": "user",
                            "content": [
                                {"image": parent_image_path},
                                {"image": current_image_path},
                                {"text": question}
                            ]
                        },
                    ]
                    response = dashscope.MultiModalConversation.call(model='qwen-vl-max',
                                                     messages=messages) 
                    print(response)
                    try:
                        response = response['output']['choices'][0]['message']['content'][0]['text']
                    except (KeyError, TypeError, IndexError):
                        response = ""

                print(response)   
                match1 = re.search(r'\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\]', response)
                if match1:
                    bounds1 = [match1.group(1), match1.group(2)]
                    # 解析bounds字符串"[x1,y1][x2,y2]"
                    x1_pred, y1_pred = map(int, bounds1[0].split(','))
                    x2_pred, y2_pred = map(int, bounds1[1].split(','))
                    if args.model == "qwen-vl":
                        x1_pred, y1_pred, x2_pred, y2_pred = (
                                    int(x1_pred / 1000 * w),
                                    int(y1_pred / 1000 * h),
                                    int(x2_pred / 1000 * w),
                                    int(y2_pred / 1000 * h)
                                    )
                    result = calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, output)
                else:
                    match1 = re.search(r'\(([0-9]+,[0-9]+)\),\(([0-9]+,[0-9]+)\)', response)
                    if match1:
                        bounds1 = [match1.group(1), match1.group(2)]
                        # 解析bounds字符串"(x1,y1),(x2,y2)"
                        x1_pred, y1_pred = map(int, bounds1[0].split(','))
                        x2_pred, y2_pred = map(int, bounds1[1].split(','))
                        if args.model == "qwen-vl":
                            x1_pred, y1_pred, x2_pred, y2_pred = (
                                    int(x1_pred / 1000 * w),
                                    int(y1_pred / 1000 * h),
                                    int(x2_pred / 1000 * w),
                                    int(y2_pred / 1000 * h)
                                    )
                        result = calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, output)
                    else:
                        result = 0
                        print("未匹配")

                acc_result = calculate_ocr(response, output)
                # print(current_image_path)
                total += acc_result
                iou_total += result
                n += 1
                print("[Action OCR Accuracy]:", total / n)
                print("[Action IOU Accuracy]:", iou_total / n)
                data = {
                    "subpath": subdir_path,
                    "predict answer" : response,
                    "target answer" : output,
                    "ocr_acc": acc_result,
                    "iou_acc": result,
                    "Action IOU Accuracy" : iou_total / n,
                    "Action OCR Accuracy" : total / n
                }
                all_data.append(data)
    with open(output_path, "w", encoding='UTF-8') as fp:
        json.dump(all_data, fp, ensure_ascii=False, indent=4)
