#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
from transformers.generation import GenerationConfig
import torch
import re
import os
import numpy as np
from tqdm import tqdm
import json
import argparse
from test_515_prompt import *
from gpt import *
from sklearn.metrics import f1_score
import torchvision.transforms as T
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
from datasets import load_dataset
import pandas as pd
import io
import spacy
# from data.template.template_cn_multi import *
# 
w = 720
h = 1280 
# nlp = spacy.load("zh_core_web_sm")
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
    return 
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

def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        return width, height

def convert_relative_to_absolute(relative_x, relative_y, image_width, image_height):
    # print(relative_x)
    absolute_x = int(relative_x * image_width)
    absolute_y = int(relative_y * image_height)
    return absolute_x, absolute_y

def preprocess(text):
    doc = nlp(text.lower())
    return [token.text for token in doc if not token.is_punct and not token.is_stop]

def calculate_f1_score(predicted_answer, true_answer):
    """
    计算 F1 指标。
    
    :param predicted_answer: 预测答案
    :param true_answer: 标准答案
    :return: F1 指标
    """
    # 将答案拆分为字符列表
    predicted_chars = list(predicted_answer)
    true_chars = list(true_answer)

    # 计算交集字符数
    common = set(predicted_chars) & set(true_chars)
    num_common = sum(min(predicted_chars.count(c), true_chars.count(c)) for c in common)

    # 计算精确率和召回率
    precision = num_common / len(predicted_chars) if len(predicted_chars) > 0 else 0
    recall = num_common / len(true_chars) if len(true_chars) > 0 else 0

    # 计算 F1 指标
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return f1
def get_parser():
    parser = argparse.ArgumentParser(description="Agent for mobile phone")
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
    parser.add_argument('--model', type=str, default='checkpoint518-6000', help='model to use')
    parser.add_argument('--dataset', type=str, default='/home/corpus/dataset/chineseocrbench/0000.parquet', help='dataset to use')
    parser.add_argument('--imagepath', type=str, default='/home/corpus/dataset/chineseocrbench', help='test json to use')
    parser.add_argument('--output_dir', type=str, default='/home/corpus/test_515/result/chineseocrbench/chineseocrbench_ckpt6000.json', help='dataset to use')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    torch.manual_seed(1234)
    model_path = None
    if args.model == "checkpoint531-600":
        model_path = "/home/corpus/ckpt/qwen_stage3_Screen_0531/checkpoint-600"
    elif args.model == "qwen-vl":
        model_path = "/home/corpus/ckpt/Qwen-VL-Chat"
    elif args.model == "checkpoint518-6000":
        model_path = "/home/corpus/ckpt/qwen_stage1_3task_0518/checkpoint-6000"
    elif args.model == "Internvl":
        model_path = '/home/corpus/open_source_model/InternVL'
    elif args.model == "chinesellava":
        model_path = "/home/corpus/open_source_model/Chinses-LLaVA"
        
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
        

    base_path = args.dataset
    output_path = args.output_dir
    all_data = []
    total_iou = 0
    total_f1 = 0
    count = 0 
    test_data = pd.read_parquet(base_path)
    print(test_data.head())
    image_dir = os.path.join(args.imagepath, f'images')
    os.makedirs(image_dir, exist_ok=True)
    # for index, row in tqdm(test_data.iterrows()):
    #     # 获取图像字节数据
    #     image_bytes = row['image']['bytes']
    #     id = row["id"]
    #     # 将字节数据转换为图像
    #     image = Image.open(io.BytesIO(image_bytes))
    #     # 生成图像文件路径
    #     image_path = os.path.join(image_dir, f'image_{id}.png')
    
    #     # 保存图像
    #     image.save(image_path)

    # # 使用 tqdm 显示进度条
    for index, example in tqdm(test_data.iterrows(), desc="Processing test data"):
        image_id = example['id']
        question = example['question']
        # question = '描述这个界面的组成，包括所有可见的文字。'
        gt_answers = example['answers']
        image_path = os.path.join(image_dir, f'image_{image_id}.png')
        
        if args.model.startswith("checkpoint531") or args.model.startswith("checkpoint518"): 
            query = tokenizer.from_list_format([
                {'text': f"中文回答下面的问题，尽量简短，不要回答无关的内容。{question}"},
                {'image': image_path},
            ])
            response, history = model.chat(tokenizer, query=query, history=None)
            print(question)
            print("response:", response)
            predicted_answer = re.findall(r'<ref>(.*?)</ref>', response)
        elif args.model == "qwen-vl":
            query = tokenizer.from_list_format([
                {'image': image_path},
                {'text': f"{question},用中文回答问题，尽量简短，不要说无关内容。"},
            ])
            response, history = model.chat(tokenizer, query=query, history=None)
            predicted_answer = response.strip()
        elif args.model == "gpt-4o":
            response = gpt_4v_screenqa(f"中文回答下面的问题，尽量简短，不要回答无关的内容。{question}", image_path)
            predicted_answer = response['response']
            if count > 1000:
                break
        elif args.model == "Internvl":
            pixel_values = load_image(image_path, max_num=6).to(torch.bfloat16).cuda()
            response = model.chat(tokenizer, pixel_values, f"{question},用中文回答问题，尽量简短，不要说无关内容。", generation_config)
            predicted_answer = response.strip()
        
        best_f1 = 0
        if isinstance(predicted_answer, list):
            for pred in predicted_answer:
                f1_scores = calculate_f1_score(pred, gt_answers)
                best_f1 = max(f1_scores, best_f1)
        else:
            f1_scores = calculate_f1_score(predicted_answer, gt_answers)
            best_f1 = f1_scores
        total_f1 += best_f1
        count += 1
        print(predicted_answer)
        print(gt_answers)
        print(f1_scores)
        print("average_f1", total_f1 / count)
        data = {
            "image_id": image_id,
            "question": question,
            "predict_answer": predicted_answer,
            "ground_truth" : gt_answers,
            "best_f1": best_f1,
            "average_f1": total_f1 / count
        }
        all_data.append(data)
        if count % 500 == 0:
            with open(output_path, "w", encoding='UTF-8') as fp:
                json.dump(all_data, fp, ensure_ascii=False, indent=4)
    
    with open(output_path, "w", encoding='UTF-8') as fp:
        json.dump(all_data, fp, ensure_ascii=False, indent=4)
