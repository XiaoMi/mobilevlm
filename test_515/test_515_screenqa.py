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

def compute_f1(predicted_answer, true_answer):
    """
    计算 F1 指标。
    
    :param predicted_answer: 预测答案
    :param true_answer: 标准答案
    :return: F1 指标
    """
    if "无人应答" in true_answer:
        return 1
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


def get_parser():
    parser = argparse.ArgumentParser(description="Agent for mobile phone")
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
    parser.add_argument('--model', type=str, default='gpt-4o', help='model to use')
    parser.add_argument('--dataset', type=str, default='/home/corpus/dataset/Rico/combined', help='dataset to use')
    parser.add_argument('--annotation', type=str, default='/home/corpus/dataset/screen_qa-main/answers_and_bboxes/translated_test.json', help='test json to use')
    parser.add_argument('--output_dir', type=str, default='/home/corpus/test_515/result/screenqa/screenqa_stage1ablation.json', help='dataset to use')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    torch.manual_seed(1234)
    model_path = None
    if args.model == "checkpoint511-1200":
        model_path = "/home/corpus/ckpt/qwen_stage3_ScreenSelf_0511/checkpoint-1000"
    elif args.model == "qwen-vl":
        model_path = "/home/corpus/ckpt/Qwen-VL-Chat"
    elif args.model == "checkpoint531-600":
        model_path = "/home/corpus/ckpt/qwen_stage3_Screen_0531/checkpoint-600"
    elif args.model == "checkpoint531-qwenablation":
        model_path = "/home/corpus/ckpt/qwen_stage3_Screen_QwenVL_e5_0606/checkpoint-1200"
    elif args.model == "Internvl":
        model_path = '/home/corpus/open_source_model/InternVL'
    elif args.model == "chinesellava":
        model_path = "/home/corpus/open_source_model/Chinses-LLaVA"
    elif args.model == 'checkpoint603-stage1ablation':
         model_path = "/home/corpus/ckpt/qwen_stage3_ScreenQA_stage1ckpt4800_e5_0610/checkpoint-600"
        
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
    total_iou = 0
    total_f1 = 0
    count = 0 
    with open(args.annotation, 'r', encoding='utf-8') as file:
        annotations = json.load(file)
    for annotation in tqdm(annotations, desc="Processing annotations"):
        image_id = annotation['image_id']
        question = annotation['question']
        gt_answers = [gt['full_answer'] for gt in annotation['ground_truth']]
        # gt_boxes = [elem['bounds'] for gt in annotation['ground_truth'] for elem in gt['ui_elements']]
        
        image_path = os.path.join(root_dir, f"{image_id}.jpg")
        
        if os.path.exists(image_path):
            if args.model.startswith("checkpoint603"): 
                query = tokenizer.from_list_format([
                    {'image': image_path},
                    {'text': question},
                ])
                response, history = model.chat(tokenizer, query=query, history=None)
                pattern = re.compile(r'(.*?)<ref>')
                match = pattern.search(response)
                if match:
                    predicted_answer = match.group(1).strip() 
                else:
                    predicted_answer = response.strip()
            elif args.model == "qwen-vl":
                query = tokenizer.from_list_format([
                    {'image': image_path},
                    {'text': question},
                ])
                response, history = model.chat(tokenizer, query=query, history=None)
                predicted_answer = response.strip()
            elif args.model == "gpt-4o":
                if count >= 2000:  # 控制测试成本；
                    break
                # response = gpt_4v_screenqa(f"回答下面的问题，尽量简短，不要说无关的内容。{question}", image_path)
                response = gpt_4v_screenqa(f"回答下面的问题，尽量简短，不要说无关的内容。{question}")
                predicted_answer = response['response']
            elif args.model == "Internvl":
                pixel_values = load_image(image_path, max_num=6).to(torch.bfloat16).cuda()
                response = model.chat(tokenizer, pixel_values, question, generation_config)
                predicted_answer = response.strip()
                

            f1_scores = [compute_f1(predicted_answer, gt) for gt in gt_answers]
            best_f1 = max(f1_scores)
            total_f1 += best_f1
            print(predicted_answer)
            print(gt_answers)
            
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
                "image_id": image_id,
                "question": question,
                "predict_answer": predicted_answer,
                "ground_truth" : gt_answers,
                "best_f1": best_f1,
                "average_f1": average_f1,
                # "average_iou": average_iou
            }
            all_data.append(data)
    
    with open(output_path, "w", encoding='UTF-8') as fp:
        json.dump(all_data, fp, ensure_ascii=False, indent=4)
