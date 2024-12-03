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
import time
import dashscope
dashscope.api_key=""
# from data.template.template_cn_multi import *
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

def parse_controls(text):  # 先做一个划分
    sections = {"click": [], "input": [], "scroll": []}
    current_section = None

    for line in text.splitlines():
        if line.startswith("可点击控件有"):
            current_section = "click"
        elif line.startswith("可输入控件有"):
            current_section = "input"
        elif line.startswith("可滚动控件有"):
            current_section = "scroll"
        elif current_section and line.strip():
            sections[current_section].append(line.strip())
    return sections

def calculate_iou(predict, target):
    predict_sections = parse_controls(predict)
    target_sections = parse_controls(target)
    
    iou_scores = {}
    total_correct = 0
    total_target = 0
    
    for key in target_sections.keys():
        predict_set = set(predict_sections[key])
        target_set = set(target_sections[key])
        
        if not target_set:
            iou_scores[key] = 0
        else:
            intersection_count = len(predict_set & target_set)
            target_count = len(target_set)
            total_correct += len(predict_set & target_set)
            total_target += len(target_set)
    
    iou_score = total_correct / total_target if total_target > 0 else 0        
    return iou_score

def parse_ocrs(text):  # 先做一个划分
    sections = {"click": [], "input": [], "scroll": []}
    current_section = None
    
    for line in text.splitlines():
        if line.startswith("可点击控件有"):
            current_section = "click"
        elif line.startswith("可输入控件有"):
            current_section = "input"
        elif line.startswith("可滚动控件有"):
            current_section = "scroll"
        elif current_section and line.strip():
            match = re.search(r'<ref>([^,]+)</ref>', line)
            if match:
                text_match = match.group(1)
                sections[current_section].append(text_match)
            else:
                sections[current_section].append(line.strip())
    
    return sections

def calculate_ocr(predict, target):
    predict_sections = parse_ocrs(predict)
    target_sections = parse_ocrs(target)
    
    iou_scores = {}
    total_correct = 0
    total_target = 0
    
    for key in target_sections.keys():
        predict_set = set(predict_sections[key])
        target_set = set(target_sections[key])
        
        if not target_set:
            iou_scores[key] = 0
        else:
            intersection_count = len(predict_set & target_set)
            target_count = len(target_set)
            total_correct += len(predict_set & target_set)
            total_target += len(target_set)
    
    iou_score = total_correct / total_target if total_target > 0 else 0        
    return iou_score


def get_parser():
    parser = argparse.ArgumentParser(description="Agent for mobile phone")
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
    parser.add_argument('--model', type=str, default='gpt-4o', help='model to use')
    parser.add_argument('--dataset', type=str, default='/home/corpus/test_515/test_data/unseen_data/actionspace_test', help='dataset to use')
    parser.add_argument('--output_dir', type=str, default='/home/corpus/test_515/result/actionspace/unseen_actionspace_gpt4o.json', help='dataset to use')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    torch.manual_seed(1234)
    model_path = None
    if args.model == "checkpoint518-6000":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-6000"
    elif args.model == "qwen-vl":
        model_path = "/home/corpus/ckpt/Qwen-VL-Chat"
    elif args.model == "checkpoint518-5400":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-5400"
    elif args.model == "checkpoint518-6400":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-6400"
    elif args.model == "checkpoint518-7000":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-7000"
    elif args.model == "Internvl":
        model_path = '/home/corpus/open_source_model/InternVL'
    elif args.model == "chinesellava":
        model_path = "/home/corpus/open_source_model/Chinses-LLaVA"
    elif args.model == "checkpoint518-200":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-200"
    elif args.model == "checkpoint518-400":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-400"
    elif args.model == "checkpoint518-600":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-600"
    elif args.model == "checkpoint518-2200":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-2200"
        
    # Ensure that the directory contains necessary files
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
    ocr_total = 0
    subdirs = [subdir for subdir in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, subdir))]
    n = 0 
    for subdir in tqdm(subdirs, desc="Processing subdirectories"):
        subdir_path = os.path.join(root_dir, subdir)
        # print(subdir_path)
        if os.path.isdir(subdir_path):
            current_input_filename = f"{subdir}-input.txt"
            current_output_filename = f"{subdir}-output.txt"
            current_image_filename = f"{subdir}-screen.png"
            current_input_path = os.path.join(subdir_path, current_input_filename)
            current_output_path = os.path.join(subdir_path, current_output_filename)
            current_image_path = os.path.join(subdir_path, current_image_filename)
            if os.path.exists(current_image_path):
                if args.model.startswith("checkpoint518"):
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        input = file.read()
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    query = tokenizer.from_list_format([
                    {'image': current_image_path}, # Either a local path or an url
                    {'text': input},
                                        ])
                elif args.model == "qwen-vl":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    input = actionspace_qwen_prompt
                    query = tokenizer.from_list_format([
                        {'text': input},
                        {'text':"问：图片："},
                        {'image': current_image_path}, # Either a local path or an url
                        {'text': f"{question}\n 答："},
                                        ])
                elif args.model == "gpt-4o":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    image_path1 = '/home/corpus/test_515/few_shot/actionspace/baicizhan0_5_50_363_357_1117/baicizhan0_5_50_363_357_1117-screen.png'
                    text1 = '在这个页面上，哪些部分可以响应用户的操作？'
                    ans1 = '''
                    可点击控件有
                    click(<ref>确认订单</ref><box>[0,64][720,112]</box>)
                    click(<ref>收货地址</ref><box>[46,198][674,242]</box>)
                    click(<ref>您还没有收货地址，请点击添加</ref><box>[46,248][674,288]</box>)
                    click(<ref>百词斩单词机，随时随地背单词！</ref><box>[238,394][544,466]</box>)
                    click(<ref>小白沙</ref><box>[238,478][544,514]</box>)
                    click(<ref>x 1</ref><box>[238,528][270,564]</box>)
                    click(<ref>¥ 219.00</ref><box>[558,394][674,426]</box>)
                    click(<ref>商品总价</ref><box>[46,612][170,650]</box>)
                    click(<ref>219.00</ref><box>[576,612][674,650]</box>)
                    click(<ref>邮费满50包邮</ref><box>[46,696][230,744]</box>)
                    click(<ref>0.00</ref><box>[612,700][674,738]</box>)
                    click(<ref>优惠券</ref><box>[46,790][140,826]</box>)
                    click(<ref>无可用优惠券</ref><box>[458,788][644,828]</box>)
                    click(<ref>cop-icon0.D5qF</ref><box>[46,874][150,918]</box>)
                    click(<ref>铜板不足或该商品无铜板抵扣</ref><box>[274,878][674,914]</box>)
                    click(<ref>订单备注</ref><box>[46,966][170,1002]</box>)
                    click(<ref>支付宝支付</ref><box>[46,1110][270,1162]</box>)
                    click(<ref>实付款¥219</ref><box>[22,1106][204,1138]</box>)
                    click(<ref>付款</ref><box>[408,1080][698,1166]</box>)
                    可输入控件有
                    input(第1个空白输入框, <box>[212,956][674,1012]</box>)
                    可滚动控件有
                    scroll(<box>[0,130][720,1184]</box>,up)
                    scroll(<box>[0,130][720,1184]</box>,down)
                    scroll(<box>[0,130][720,1184]</box>,left)
                    scroll(<box>[0,130][720,1184]</box>,right)
                    '''
                    time.sleep(30)
                    response = gpt_4v_actionspace(text1, image_path1, ans1, question, current_image_path)
                    print(response)
                    response = response['response']
                if args.model != "gpt-4o":
                    response, history = model.chat(tokenizer, query=query, history=None)
                iou_result = calculate_iou(response, output)
                ocr_result = calculate_ocr(response, output)
                
                print(response)
                total += iou_result
                ocr_total += ocr_result
                n += 1
                print("[average IOU]:", total / n)
                print("[average OCR]:", ocr_total / n)
                data = {
                    "subpath": subdir_path,
                    "predict answer" : response,
                    "target answer" : output,
                    "aveIOU" : total / n,
                    "aveOCR" : ocr_total / n
                }
                all_data.append(data)
                if n % 100 == 0:
                    with open(output_path, "w", encoding='UTF-8') as fp:
                        json.dump(all_data, fp, ensure_ascii=False, indent=4)
    with open(output_path, "w", encoding='UTF-8') as fp:
        json.dump(all_data, fp, ensure_ascii=False, indent=4)

