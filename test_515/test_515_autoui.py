#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
from transformers.generation import GenerationConfig
import torch
import psutil
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
import csv
import time
from datetime import datetime
from torchvision.transforms.functional import InterpolationMode
# from data.template.template_cn_multi import *
import spacy
# from data.template.template_cn_multi import *
nlp = spacy.load("en_core_web_sm")
w = 720
h = 1280 
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
# 获取当前进程的PID
current_pid = os.getpid()

# 定义记录文件名
log_file = "model_resource_usage_log.csv"

# 初始化csv文件并写入表头
with open(log_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "CPU_Usage(%)", "RAM_Usage(MB)", "GPU_Allocated(MB)", "GPU_Reserved(MB)"])

# 定义记录资源使用情况的函数
def log_resource_usage(pid):
        process = psutil.Process(pid)
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取CPU和RAM使用情况
        cpu_usage = process.cpu_percent(interval=1)
        ram_usage = process.memory_info().rss / (1024 ** 2)  # 转换为MB

        # 获取GPU使用情况
        gpu_allocated = torch.cuda.memory_allocated() / (1024 ** 2)  # 转换为MB
        gpu_reserved = torch.cuda.memory_reserved() / (1024 ** 2)  # 转换为MB

        # 将数据写入csv文件
        with open(log_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, cpu_usage, ram_usage, gpu_allocated, gpu_reserved])

        # 每30秒记录一次
        # time.sleep(30)
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



image_width, image_height = 412, 732

def convert_absolute_to_relative(x, y, width, height):
    return x / width, y / height

def preprocess(text):
    doc = nlp(text.lower())
    return [token.text for token in doc if not token.is_punct and not token.is_stop]

def calculate_f1_score(pred_text, true_text):
    # 将输入文本转换为小写
    pred_text = pred_text.lower()
    true_text = true_text.lower()

    # 如果小写的预测文本是答案的一部分，直接返回 1
    if pred_text in true_text:
        return 1.0

    # 否则，计算 F1 分数
    pred_tokens = set(preprocess(pred_text))
    true_tokens = set(preprocess(true_text))

    if len(pred_tokens) == 0 or len(true_tokens) == 0:
        return 0.0

    # 计算 Precision 和 Recall
    common_tokens = pred_tokens & true_tokens
    precision = len(common_tokens) / len(pred_tokens)
    recall = len(common_tokens) / len(true_tokens)
    
    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)

def calculate_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

def evaluate_action(pred_action, true_action, image_width, image_height):
    pattern = r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]'
    pred_match = re.search(pattern, pred_action)
    true_match = re.search(pattern, true_action)
    if not isinstance(pred_action, (str, bytes)) or not isinstance(true_action, (str, bytes)): 
        return 1
    if true_action == "STATUS_TASK_COMPLETE": # single使用 # 原数据用prompt指示single只执行一步动作。
        return 1

    if "click" in pred_action and "click" in true_action:
        if pred_match and true_match:
            pred_touch = [float(pred_match.group(1)), float(pred_match.group(2))]
            true_touch = [float(true_match.group(1)), float(true_match.group(2))]

            pred_touch_rel = convert_absolute_to_relative(pred_touch[0], pred_touch[1], image_width, image_height)
            true_touch_rel = convert_absolute_to_relative(true_touch[0], true_touch[1], image_width, image_height)
            print("distance", calculate_distance(pred_touch_rel, true_touch_rel))
            return 1 if calculate_distance(pred_touch_rel, true_touch_rel) <= 0.14 else 0

    elif "scroll" in pred_action and "scroll" in true_action:
        pred_direction_match = re.search(r'scroll.*</box>,\s(\w+)\)', pred_action)
        true_direction_match = re.search(r'scroll.*</box>,\s(\w+)\)', true_action)
        
        if pred_direction_match and true_direction_match:
            pred_direction = pred_direction_match.group(1)
            true_direction = true_direction_match.group(1)
            return 1 if pred_direction == true_direction else 0
        else:
            # Handle the case where direction matches are None
            return 0

    elif "type" in pred_action and "type" in true_action:
        pred_text_match = re.search(r'type\((.*)\)', pred_action)
        true_text_match = re.search(r'type\((.*)\)', true_action)
        
        if pred_text_match and true_text_match:
            pred_text = pred_text_match.group(1)
            true_text = true_text_match.group(1)
            return calculate_f1_score(pred_text, true_text)
        else:
            # Handle the case where text matches are None
            return 0

    elif "special_action" in pred_action and "special_action" in true_action:
        return 1 if pred_action == true_action else 0

    elif "STATUS_TASK_COMPLETE" in pred_action and "STATUS_TASK_COMPLETE" in true_action:
        return 1 if pred_action == true_action else 0

    return 0
def convert_actions(action):
    result = None
    touch_point = [1, 1]
    lift_point = [1, 1]
    action_type = action["action_type"]
    touch = action.get("touch_point")
    lift = action.get("lift_point")
    typed_text = action.get("typed_text", "")
    pattern = r'\[(\d+\.\d+), (\d+\.\d+)\]'

    # 使用正则表达式进行匹配
    match = re.search(pattern, touch)

    if match:
        touch_point[0] = float(match.group(1))
        touch_point[1] = float(match.group(2))
    
    # 使用正则表达式进行匹配
    match = re.search(pattern, lift)

    if match:
        lift_point[0] = float(match.group(1))
        lift_point[1] = float(match.group(2))
    
    # print(touch_point[0], touch_point[1])


    if action_type == "DUAL_POINT":
        touch_point[0], touch_point[1] = convert_relative_to_absolute(touch_point[0], touch_point[1], image_width, image_height)
        lift_point[0], lift_point[1] = convert_relative_to_absolute(lift_point[0], lift_point[1], image_width, image_height)
        if touch_point == lift_point:
            return f"click(<ref></ref><box>[{touch_point[0]},{touch_point[1]}][{lift_point[0]},{lift_point[1]}]</box>)"
        else:
            direction = ""
            if touch_point[1] > lift_point[1]:
                direction = "up"
            elif touch_point[1] < lift_point[1]:
                direction = "down"
            elif touch_point[0] > lift_point[0]:
                direction = "left"
            elif touch_point[0] < lift_point[0]:
                direction = "right"
            return f"scroll(<box>[{touch_point[0]},{touch_point[1]}][{lift_point[0]},{lift_point[1]}]</box>, {direction})"
    
    elif action_type == "TYPE":
        return f"type({typed_text})"
    
    elif action_type == "PRESS_BACK" or action_type == "PRESS_ENTER" or action_type == "PRESS_HOME":
        return f"special_action({action_type})"
    elif action_type == "STATUS_TASK_COMPLETE":
        return f"STATUS_TASK_COMPLETE"
        
    return result

def process_achis(action_history):
    result = []

    for action in action_history[:-1]:
        action = "{" + action + "}"
        action = json.loads(action)
        action_pro = convert_actions(action)
        result.append(action_pro)
    return result


def generate_input(input):
    instruction = input["goal_cn"]
    action_history = input["action_history"]
    result = process_achis(action_history)
    return f"你需要完成如下任务：{instruction}。已完成的动作如下：" + "\n".join(result)

def generate_input_en(input):
    instruction = input["goal"]
    action_history = input["action_history"]
    result = process_achis(action_history)
    return f"You need to finish the following task：{instruction}。The completed actions are as follows：" + "\n".join(result)

def generate_output(output):
    output = "{" + output["target_action"] + "}"
    action = json.loads(output)
    return convert_actions(action)
                        
def get_parser():
    parser = argparse.ArgumentParser(description="Agent for mobile phone")
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
    parser.add_argument('--model', type=str, default='checkpoint603-mixture', help='model to use')
    parser.add_argument('--dataset', type=str, default='/home/corpus/Auto-UI-main/dataset/blip/web_shopping_blip_test', help='dataset to use')
    parser.add_argument('--imagepath', type=str, default='/home/corpus/Auto-UI-main/dataset/t5/web_shopping_blip_test', help='test json to use')
    parser.add_argument('--output_dir', type=str, default='/home/corpus/test_515/result/auto-ui/autoui_web_shopping_603-en-GPUTEST.json', help='dataset to use')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    torch.manual_seed(1234)
    # log_resource_usage(current_pid)
    model_path = None
    if args.model == "checkpoint603-googleseperate":
        model_path = "/home/corpus/ckpt/qwen_stage3_google_ckpt3300_e1_0608/checkpoint-800"
    elif args.model == "checkpoint603-installseperate":
        model_path = "/home/corpus/ckpt/qwen_stage3_install_ckpt3300_e1_0609/checkpoint-500"
    elif args.model == "checkpoint603-mixture":
        model_path = "/home/corpus/ckpt/qwen_stage3_4task_ckpt6000_e1_0603/checkpoint-1800"
    elif args.model == "Internvl":
        model_path = '/home/corpus/open_source_model/InternVL'
    elif args.model == "checkpoint603-singleseperate":
        model_path = "/home/corpus/ckpt/qwen_AutoUI_single_stage1ckpt4800_e6_0613/checkpoint-200"
    elif args.model == 'checkpoint603-qwenablation':
        model_path = "/home/corpus/ckpt/qwen_stage3_4task_QwenVL_e1_0603/checkpoint-2400"
    elif args.model == 'checkpoint603-stage1ablation':
         model_path = "/home/corpus/ckpt/qwen_AutoUI_4task_stage1ckpt4800_e1_0610/checkpoint-1300"
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
    base_image_path = args.imagepath
    output_path = args.output_dir
    all_data = []
    total_iou = 0
    total_f1 = 0
    count = 0 
    episode_dirs = [episode_dir for episode_dir in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, episode_dir))]
    turn = 0 
    # # 使用 tqdm 显示进度条
    for episode_dir in tqdm(episode_dirs, desc="Processing episodes"):
        process = psutil.Process(current_pid)
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取CPU和RAM使用情况
        cpu_usage = process.cpu_percent(interval=1)
        ram_usage = process.memory_info().rss / (1024 ** 2)  # 转换为MB

        # 获取GPU使用情况
        gpu_allocated = torch.cuda.memory_allocated() / (1024 ** 2)  # 转换为MB
        gpu_reserved = torch.cuda.memory_reserved() / (1024 ** 2)  # 转换为MB

        # 将数据写入csv文件
        with open(log_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, cpu_usage, ram_usage, gpu_allocated, gpu_reserved])
        episode_path = os.path.join(base_path, episode_dir)
        episode_image_path = os.path.join(base_image_path, episode_dir)
        # print(episode_image_path)
        turn += 1
        # if turn < 678:
        #     continue
        if os.path.isdir(episode_path):
            # 遍历每个 episode 目录下的 step 目录
            for step_dir in os.listdir(episode_path):
                step_path = os.path.join(episode_path, step_dir)
                step_image_path = os.path.join(episode_image_path, step_dir)
                if os.path.isdir(step_path):
                    meta_data_path = os.path.join(step_path, "meta_data.json")
                    image_path = os.path.join(step_image_path, "image.png")
                    print(meta_data_path)
                    print(image_path)
                    if os.path.exists(meta_data_path):
                        try:
                            with open(meta_data_path, "r", encoding='UTF-8') as fp:
                                metadata = json.load(fp)
                                question = generate_input_en(metadata)
                                output = generate_output(metadata)
                                if output is None:
                                    continue
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from file {meta_data_path}: {e}")
                            continue
        
                    if os.path.exists(image_path):
                        if args.model.startswith("checkpoint529") or args.model.startswith("checkpoint603"): 
                            query = tokenizer.from_list_format([
                                {'image': image_path},
                                {'text': question},
                            ])
                            response, history = model.chat(tokenizer, query=query, history=None)
                            predicted_answer = response.strip()
                        elif args.model == "qwen-vl":
                            query = tokenizer.from_list_format([
                                {'image': image_path},
                                {'text': question},
                            ])
                            response, history = model.chat(tokenizer, query=query, history=None)
                            predicted_answer = response.strip()
                        elif args.model == "gpt-4o":
                            response = gpt_4v_screenqa(f"回答下面的问题，尽量简短，不要说无关的内容。{question}", image_path)
                            predicted_answer = response['response']
                        elif args.model == "Internvl":
                            pixel_values = load_image(image_path, max_num=6).to(torch.bfloat16).cuda()
                            response = model.chat(tokenizer, pixel_values, question, generation_config)
                            predicted_answer = response.strip()
                            

                        # f1_scores = [compute_f1(predicted_answer, gt) for gt in gt_answers]
                        # best_f1 = max(f1_scores)
                        # total_f1 += best_f1
                        f1_score = evaluate_action(predicted_answer, output, 412, 732) 
                        print(predicted_answer)
                        print(output)
                        print(f1_score)
                        total_f1 += f1_score
                        
                        # match = re.search(r'\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\]', response)
                        # if match:
                        #     bounds = [match.group(1), match.group(2)]
                        #     x1_pred, y1_pred = map(int, bounds[0].split(','))
                        #     x2_pred, y2_pred = map(int, bounds[1].split(','))
                        #     iou = [calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, gt) for gt in gt_boxes]
                        #     best_iou = max(iou)
                        #     total_iou += best_iou
                        # else:
                        #     total_iou += 0
                        #     print("未匹配成功！")

                        count += 1
                        # average_iou = total_iou / count
                        average_f1 = total_f1 / count
                        print(f"[average F1]: {average_f1}")

                        data = {
                            "image_id": meta_data_path,
                            "question": question,
                            "predict_answer": predicted_answer,
                            "ground_truth" : output,
                            "best_f1": f1_score, 
                            "average_f1": average_f1,
                        }
                        all_data.append(data)
                        if count % 500 == 0:
                            with open(output_path, "w", encoding='UTF-8') as fp:
                                json.dump(all_data, fp, ensure_ascii=False, indent=4)
    
    with open(output_path, "w", encoding='UTF-8') as fp:
        json.dump(all_data, fp, ensure_ascii=False, indent=4)
