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
'''
# 1st dialogue turn
query = tokenizer.from_list_format([
    {'image': '/zk/corpus/arm_01/ctrip_graph_8100/ctrip0_0/ctrip0_0-screen.png'}, # Either a local path or an url
    {'text': '<actions> 可点击控件有click(资质说明)\nclick(国内)\nclick(海外)\nclick(国内･海外)\nclick(钟点･月租)\nclick(民宿)\nclick(上海)\nclick(位置/品牌/酒店)\nclick(3月2日)\nclick(今天)\nclick(3月3日)\nclick(明天)\nclick(共1晚)\nclick(1间房 1成人 0儿童)\nclick(价格/星级)\nclick(贵宾专享)\nclick(迪士尼)\nclick(外滩)\nclick(积分当钱花)\nclick(浦东国际机场)\nclick(查 询)\nclick(口碑榜)\nclick(城市精选)\nclick(特价套餐)\nclick(随时退)\nclick(超值低价)\nclick(7折起)\nclick(10)\nclick(购物车/收藏)\nclick(我的权益)\nclick(我的点评)\nclick(我的订单)\n可输入控件有\n可滚动控件有scroll([0,0][720,1184],up)\nscroll([0,0][720,1184],down)\nscroll([0,0][720,1184],left)\nscroll([0,0][720,1184],right)\nscroll([0,0][720,360],up)\nscroll([0,0][720,360],down)\nscroll([0,0][720,360],left)\nscroll([0,0][720,360],right)\nscroll([64,692][656,801],up)\nscroll([64,692][656,801],down)\nscroll([64,692][656,801],left)\nscroll([64,692][656,801],right)\nscroll([24,1089][696,1184],up)\nscroll([24,1089][696,1184],down)\nscroll([24,1089][696,1184],left)\nscroll([24,1089][696,1184],right) </actions>\n这是什么?'},
])
response, history = model.chat(tokenizer, query=query, history=None)
print(response)
# 图中是一名女子在沙滩上和狗玩耍，旁边是一只拉布拉多犬，它们处于沙滩上。


query = tokenizer.from_list_format([
    {'image': '/zk/corpus/arm_01/ctrip_graph_8100/ctrip0_0/ctrip0_0-screen.png'}, # Either a local path or an url
    {'text': '<actions> 可点击控件有click(资质说明)\nclick(国内)\nclick(海外)\nclick(国内･海外)\nclick(钟点･月租)\nclick(民宿)\nclick(上海)\nclick(位置/品牌/酒店)\nclick(3月2日)\nclick(今天)\nclick(3月3日)\nclick(明天)\nclick(共1晚)\nclick(1间房 1成人 0儿童)\nclick(价格/星级)\nclick(贵宾专享)\nclick(迪士尼)\nclick(外滩)\nclick(积分当钱花)\nclick(浦东国际机场)\nclick(查 询)\nclick(口碑榜)\nclick(城市精选)\nclick(特价套餐)\nclick(随时退)\nclick(超值低价)\nclick(7折起)\nclick(10)\nclick(购物车/收藏)\nclick(我的权益)\nclick(我的点评)\nclick(我的订单)\n可输入控件有\n可滚动控件有scroll([0,0][720,1184],up)\nscroll([0,0][720,1184],down)\nscroll([0,0][720,1184],left)\nscroll([0,0][720,1184],right)\nscroll([0,0][720,360],up)\nscroll([0,0][720,360],down)\nscroll([0,0][720,360],left)\nscroll([0,0][720,360],right)\nscroll([64,692][656,801],up)\nscroll([64,692][656,801],down)\nscroll([64,692][656,801],left)\nscroll([64,692][656,801],right)\nscroll([24,1089][696,1184],up)\nscroll([24,1089][696,1184],down)\nscroll([24,1089][696,1184],left)\nscroll([24,1089][696,1184],right) </actions>\n哪个动作会带我到包含“酒店”的区域？'},
])
response, history = model.chat(tokenizer, '框出图中击掌的位置', history=history)
print(response)
'''

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
    parser.add_argument('--model', type=str, default='qwen-vl-max', help='model to use')
    parser.add_argument('--dataset', type=str, default='/home/corpus/test_515/test_data/unseen_data/ref_test', help='dataset to use')
    parser.add_argument('--output_dir', type=str, default='/home/corpus/test_515/result/grounding/seen_ref_qwenmax.json', help='dataset to use')
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
                    query = tokenizer.from_list_format([ # Either a local path or an url
                    {'image': current_image_path},
                    {'text': input},
                                    ])


                elif args.model == "qwen-vl":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    input = ref_qwen_prompt.format(image1='/home/corpus/test_58/few_shot/ref/image1/image1.png', image2='/home/corpus/test_58/few_shot/ref/image2/image2.png', image3='/home/corpus/test_58/few_shot/ref/image3/image3.png')
                    query = tokenizer.from_list_format([ # Either a local path or an url
                    {'text': input},
                    {'image': current_image_path},
                    {'text': question},
                                    ])


                elif args.model == "gpt-4v":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    text1 = '找出“翻唱”在屏幕上的位置。'
                    image_path1 = '/home/corpus/test_58/few_shot/ref/image2/image2.png'
                    ans1 = '[494,187][546,223]'
                    input = f"{question},你只需要告诉我它的检测框[x1,y1][x2,y2]即可，注意，图像尺寸为720*1280，坐标为相对于图像左上角的相对偏移量。"
                    response = gpt_4v_ref(text1, image_path1, ans1, input, current_image_path)
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    match1 = re.search(r'\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\]', response['response'])
                    if match1:
                        bounds1 = [match1.group(1), match1.group(2)]
                        # 解析bounds字符串"[x1,y1][x2,y2]"
                        x1_pred, y1_pred = map(int, bounds1[0].split(','))
                        x2_pred, y2_pred = map(int, bounds1[1].split(','))
                        result = calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, output)
                    else: 
                        result = 0
                        print("未匹配成功！")
                    print(response)
                
                elif args.model == "qwen-vl-plus":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    text1 = '找出“翻唱”在屏幕上的位置。'
                    image_path1 = '/home/corpus/test_58/few_shot/ref/image2/image2.png'
                    ans1 = '[494,187][546,223]'
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"image": current_image_path},
                                {"text": f"{question},你只需要告诉我它的检测框[x1,y1][x2,y2]即可，注意，图像尺寸为720*1280，坐标为相对于图像左上角的相对偏移量。"}
                            ]
                        }
                    ]
                    response = dashscope.MultiModalConversation.call(model='qwen-vl-plus',
                                                     messages=messages)
                    print(response)
                    try:
                        response = response['output']['choices'][0]['message']['content'][0]['text']
                    except (KeyError, TypeError, IndexError):
                        response = ""
                    
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    match1 = re.search(r'\[([0-9]+,\s*[0-9]+)\].*?\[([0-9]+,\s*[0-9]+)\]', response)
                    if match1:
                        bounds1 = [match1.group(1), match1.group(2)]
                        # 解析bounds字符串"[x1,y1][x2,y2]"
                        x1_pred, y1_pred = map(int, bounds1[0].split(','))
                        x2_pred, y2_pred = map(int, bounds1[1].split(','))
                        result = calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, output)
                    else: 
                        result = 0
                        print("未匹配成功！")
                    
                elif args.model == "qwen-vl-max":
                    with open(current_input_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    text1 = '找出“翻唱”在屏幕上的位置。'
                    image_path1 = '/home/corpus/test_58/few_shot/ref/image2/image2.png'
                    ans1 = '[494,187][546,223]'
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"image": current_image_path},
                                {"text": f"{question},你只需要告诉我它的检测框[x1,y1][x2,y2]即可，注意，图像尺寸为720*1280，坐标为相对于图像左上角的相对偏移量。"}
                            ]
                        }
                    ]
                    response = dashscope.MultiModalConversation.call(model='qwen-vl-max',
                                                     messages=messages) 
                    print(response)
                    try:
                        response = response['output']['choices'][0]['message']['content'][0]['text']
                    except (KeyError, TypeError, IndexError):
                        response = ""
                    
                    with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                    match1 = re.search(r'\[([0-9]+,\s*[0-9]+)\].*?\[([0-9]+,\s*[0-9]+)\]', response)
                    if match1:
                        bounds1 = [match1.group(1), match1.group(2)]
                        # 解析bounds字符串"[x1,y1][x2,y2]"
                        x1_pred, y1_pred = map(int, bounds1[0].split(','))
                        x2_pred, y2_pred = map(int, bounds1[1].split(','))
                        result = calculate_iou(x1_pred, y1_pred, x2_pred, y2_pred, output)
                    else: 
                        result = 0
                        print("未匹配成功！")
                    


                with open(current_output_path, 'r', encoding='utf-8') as file:
                        output = file.read()
                # print(query)
                count = 0 
                result = 0
                match1 = None
                while match1 is None and count < 3 and args.model != 'gpt-4v' and args.model != 'qwen-vl-plus' and args.model != 'qwen-vl-max': 
                    response, history = model.chat(tokenizer, query=query, history=None)
                    count += 1
                    print(response)
                    if not response.startswith('['):
                        response = '[' + response
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
                            print("未匹配")
                        
                total += result
                n += 1
                acc = total / n
                print("[average IOU]:", acc)
                data = {
                    "subpath": subdir_path,
                    "predict box" : response,
                    "target box" : output,
                    "aveIOU" : acc
                }
                all_data.append(data)
                if n > 350:
                    break
                if n % 50 == 0:
                    with open(output_path, "w", encoding='UTF-8') as fp:
                        json.dump(all_data, fp, ensure_ascii=False, indent=4)
    with open(output_path, "w", encoding='UTF-8') as fp:
        json.dump(all_data, fp, ensure_ascii=False, indent=4)



                



