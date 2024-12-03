#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.      

import os
import json
import pickle
import random
import time
import itertools

import jsonlines
import pandas as pd


from template_cn_multi import *

click_instruction = [
    "查询{text}",
    "我想查找{text}",
    "我想看{text}",
    "我想了解{text}有什么？",
    "查看{text}都有哪些",
    "查看{text}详情",
    "我想看一下{text}",
    "我想去{text}",
    "我想了解{text}",
    "查看{text}",
    "点击{text}",
    "我想看一下{text}",
    "看下{text}",
    "我想了解{text}",
    "{text}",
    "我想切换{text}",
    "帮我点击{text}选项框",
    "帮我点击{text}按钮",
    "帮我点击{text}",
    "切换{text}",
    "我想获取{text}",
    "帮我{text}",
    "选择{text}",
    "看一下{text}",
    "我想选择{text}",
    "选择{text}",
    "看一下{text}怎么办",
    "我想切换手机验证码登录",
    "查看 {text}",
    "我想了解{text} ",
    "我想选择{text}",
    "{text}有哪些",
    "看看{text}",
    "查询{text}有什么",
    "我想查看{text}",
    "我想看看{text}",
    "帮我查询{text}",
    "我想咨询一下{text}",
    "我想查看{text}的信息",
    "我想查找{text}",
    "我想看{text}有什么",
    "我想查看{text}有什么",
    "我想查找{text}",
    "展开{text}",
    "我想查看{text}页面",
    "查看一下{text}",
    "我想筛选一下{text}",
    "添加{text}",
    "看一下{text}",
    "我想看看{text}里有什么",
    "{text}里有什么",
    "想看{text}",
    "我想咨询{text}",
    "我想了解一下{text}",
    "选择{text}",
    "搜索{text}",
    "输入{text}",
    "打开{text}看一下",
    "我要{text}",
    "看看{text}有什么",
    "我想看看{text}里的内容",
    "看看{text}里的内容",
    "{text}里的内容",
    "我想按现在条件查询一下{text}",
    "查{text}",
    "我想修改{text}",
    "查查{text}",
    "查看一下{text}",
    "搜一下{text}",
    "搜一下搜{text}",
    "看看{text}有什么内容",
    "{text}有什么内容",
    "我想看看{text}里有什么",
    "我想看看{text}",
    "帮我{text}",
    "帮我勾选{text}",
    "帮我看看{text}",
    "阅览一下{text}",
    "了解一下{text}的内容",
    "查一下{text}的介绍",
    "查看一下{text}有哪些",
    "看一下{text}的情况 ",
    "打开一下{text}",
    "点一下{text}",
    "我想选择{text}",
    "我想点击{text}",
    "我想查看{text}",
    "选择{text}",
    "点击{text}",
    "查看{text}",
    "打开{text}",
    "打开{text}看看",
    "点击{text}按钮",
    "查看{text}是什么",
    "查看{text}里面有什么",
    "点{text}",
    "点击一下{text}",
    "选中{text}",
    "先选{text}",
    "我要选择{text}"
]

input_instruction = [
    "我想修改{text}",
    "我想搜索{text}",
    "输入{text}",
    "输入 {text}",
    "输入一下{text}",
    "搜索{text}",
    "我想修改{text}",
    "我想重新搜索{text}",
    "我想输入{text}",
    "我想搜索一下{text}",
    "改成{text}",
    "查找{text}",
    "查一下{text}",
    "我想查找{text}",
    "我想查一下{text}",
    "写入{text}",
    "帮我搜一下{text}",
    "帮我输入{text}",
    "在输入框里输入{text}",
    "写{text}",
    "帮我搜{text}",
    "先输入{text}",
    "先搜索{text}",
    "在输入框里写{text}",
    "在输入框里输入{text}",
    "点击输入框，输入{text}",
    "点击输入框，搜索{text}",
    "点击输入框，修改成{text}",
    "点击输入框，写入{text}",
    "点击输入框，查找{text}"
]

def save_txt(path,data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
        f.write('\n')
        f.close()
def save_dict(path,data):
    with open(path, 'w', encoding='utf-8') as f:
        datajson=json.dumps(data)
        json.dump(datajson, f, indent=4,ensure_ascii=False)
        f.write('\n')
        f.close()
def save_json(path,data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4,ensure_ascii=False)
        f.write('\n')
        f.close()

def load_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data
def load_txt(path):
    with open(path, 'r', encoding='utf-8') as file:
        all_name_path=[]
        for line in file:
            all_name_path.append(line.strip())
        return all_name_path
def load_dict(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_dict=json.loads(data)
        return data_dict
def get_action_by_id(all_action_id,id_):
    for action in all_action_id:
        if all_action_id[action]==id_:
            return action
    return None

def verify_Img(path):
    try:
        image = Image.open(path)  # 检查文件是否能正常打开
        image.verify()  # 检查文件完整性
        image.close()
    except:
        return False
    return True


def map_and_reverse_complete_interactive_elements(html_content):  # 建立元素和数值的映射关系；
    lines = html_content.split('\n')
    interactive_elements = {}
    counter = 1  # Start numbering from 1

    for line in lines:
        # Check if the line contains a clickable, scrollable or input element
        if 'clickable="true"' in line or 'scrollable="true"' in line or 'input' in line:
            # Map the entire line (HTML tag) to the number
            interactive_elements[counter] = line.strip()
            counter += 1  # Increment the counter for the next interactive element

    return interactive_elements

def display_html_and_mapping(html_content, elements_map):
    # Outputting the entire HTML content
    #print("[HTML Content]:")
    #print(html_content)
    #print("[Interactive Elements Mapping]:")
    # Initialize categories
    clickables = {}
    scrollables = {}
    inputs = {}  # Assuming we could identify input elements somehow

    # Iterating through the elements map to categorize
    for index, html in elements_map.items():
        if 'input' in html:
            inputs[index] = html
        elif 'EditText' in html:
            inputs[index] = html
        elif 'scrollable="true"' in html:
            scrollables[index] = html
        elif 'clickable="true"' in html:
            clickables[index] = html

    # Outputting categorized elements
    categories = [("Clickables", clickables), ("Scrollables", scrollables), ("Inputs", inputs)]
    action_space={}
    for category_name, category_map in categories:
        if category_map:  # Only print if category has items
            #print(f"[{category_name}]:")
            max_index_length = len(str(max(category_map.keys()))) if category_map else 0
            for index, html in category_map.items():
                description = ""
                # Extracting a brief description
                if 'description="' in html:
                    description = html.split('description="')[1].split('"')[0]
                elif 'class="' in html:
                    class_name = html.split('class="')[1].split('"')[0]
                    # Check if there is visible text inside the element
                    inner_text = html.split('>')[1].split('<')[0] if '>' in html and '<' in html else ""
                    if not inner_text.strip():
                        description = f"Empty {class_name}"
                    else:
                        description = inner_text.strip()

                # Adding bounds if the element is scrollable
                if 'scrollable="true"' in html and 'bounds="' in html:
                    bounds = html.split('bounds="')[1].split('"')[0]
                    description += f" ({bounds})" if bounds else ""

                if description:  # Only print if there's a description or text content
                    #print(f"{index:{max_index_length}}: {description}")

                    action_space[index]=category_name
    return action_space


def calculate_scroll_parameters1(window_size, html, direction, scroll_type):
    width = window_size['width']
    height = window_size['height']
    safe_margin = 10   # 安全边界距离
    match = re.search(r'bounds="\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\]"', html)
    bounds = [match.group(1), match.group(2)]
    # 解析bounds字符串"[x1,y1][x2,y2]"
    x1, y1 = map(int, bounds[0].split(','))
    x2, y2 = map(int, bounds[1].split(','))

    # 计算中点坐标
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2

    if scroll_type == 'short':
        # 短距离滚动
        offset_x = (x2 - x1) // 4
        offset_y = (y2 - y1) // 4
        scroll_coordinates = {
            'up': ([mid_x, mid_y + offset_y], [mid_x, mid_y - offset_y]),
            'down': ([mid_x, mid_y - offset_y], [mid_x, mid_y + offset_y]),
            'left': ([mid_x + offset_x, mid_y], [mid_x - offset_x, mid_y]),
            'right': ([mid_x - offset_x, mid_y], [mid_x + offset_x, mid_y])
        }
    elif scroll_type == 'long':
        # 长距离滚动
        if direction == 'up':
            start_x = end_x = mid_x
            start_y = y2 - safe_margin
            end_y = safe_margin
        elif direction == 'down':
            start_x = end_x = mid_x
            start_y = y1 + safe_margin
            end_y = height - safe_margin
        elif direction == 'left':
            start_y = end_y = mid_y
            start_x = x2 - safe_margin
            end_x = safe_margin
        elif direction == 'right':
            start_y = end_y = mid_y
            start_x = x1 + safe_margin
            end_x = width - safe_margin
        else:
            return None  # 无效方向
        scroll_coordinates = {
            direction: ([start_x, start_y], [end_x, end_y])
        }
    else:
        return None  # 无效的滚动类型

    return scroll_coordinates[direction]

    # # 定义滚动偏移量
    # offset_x = (x2 - x1) // 4
    # offset_y = (y2 - y1) // 4
    #
    # # 根据方向计算滚动起始和结束坐标
    # scroll_directions = {
    #     'up': ([mid_x, mid_y + offset_y], [mid_x, mid_y - offset_y]),
    #     'down': ([mid_x, mid_y - offset_y], [mid_x, mid_y + offset_y]),
    #     'left': ([mid_x + offset_x, mid_y], [mid_x - offset_x, mid_y]),
    #     'right': ([mid_x - offset_x, mid_y], [mid_x + offset_x, mid_y])
    # }
    #
    # return scroll_directions[direction]

def process_user_input1(window_size, user_input, elements_map):  # 将用户的输入转化为实际的执行指令
    # Splitting the input for action and parameters
    parts = user_input.split('(', 1)
    action = parts[0].strip().lower()  # Action: click, scroll, input
    params = parts[1].rstrip(')').split(',') if len(parts) > 1 else []  # Parameters in the parentheses

    # Defining the action command and parameters
    action_command = ''
    params_command = ''

    # Determine the action and construct corresponding command
    if action == 'click':
        action_command = 'click'
        if params and params[0].isdigit() and int(params[0]) in elements_map:
            params_command = elements_map[int(params[0])]
    elif action == 'press':
        action_command = 'press'
        if params and params[0].isdigit() and int(params[0]) in elements_map:
            params_command = elements_map[int(params[0])]
    elif action == 'zoom':
        action_command = 'zoom'
        if params and params[0].isdigit() and int(params[0]) in elements_map:
            params_command = elements_map[int(params[0])]
    elif action == 'pinch':
        action_command = 'pinch'
        if params and params[0].isdigit() and int(params[0]) in elements_map:
            params_command = elements_map[int(params[0])]
    elif action == 'scroll':
        action_command = 'scroll'
        # Defining scroll directions as start and end coordinates
        if params and params[0].isdigit() and int(params[0]) in elements_map:
            html_element = elements_map[int(params[0])]
            direction = str(params[1])
            if len(params) > 2:
                scroll_type = 'long'
            else:
                scroll_type = 'short'
            params_command = calculate_scroll_parameters1(window_size, html_element, direction, scroll_type)
    elif action == 'input':
        action_command = 'input'
        if params and params[0].isdigit() and int(params[0]) in elements_map:
            params_command = elements_map[int(params[0])]
            if len(params) > 1:
                params_command += f", '{params[1]}'"

    # Construct the final command
    final_command = f"{action_command}({params_command})"

    return final_command

def gen_action_list(action_space,window_size,mapping):
    action_tobe=[]
    for index in action_space:
        category_name=action_space[index]

        action_list=[]
        if category_name=="Clickables":
            action_res="click("+str(index)+")"
            action_list.append(action_res)
            
        elif category_name=="Scrollables":
            action_res="scroll("+str(index)+",up)"
            action_list.append(action_res)
            #action_res="scroll("+str(index)+",up, long)"
            #action_list.append(action_res)
            action_res="scroll("+str(index)+",down)"
            action_list.append(action_res)
            #action_res="scroll("+str(index)+",down, long)"
            #action_list.append(action_res)
            action_res="scroll("+str(index)+",left)"
            action_list.append(action_res)
            #action_res="scroll("+str(index)+",left, long)"
            #action_list.append(action_res)
            action_res="scroll("+str(index)+",right)"
            action_list.append(action_res)
            #action_res="scroll("+str(index)+",right, long)"
            #action_list.append(action_res)
        elif category_name=="Inputs":
            action_res="click("+str(index)+")"
            action_list.append(action_res)
            #random.shuffle(current_text_list)
            for temp_text in current_text_list:
                action_res="input("+str(index)+","+temp_text+")"
                if action_res not in action_list:
                    action_list.append(action_res)

        #window_size = driver.get_window_size()
        for action_res in action_list:
            action_res = process_user_input1(window_size, action_res, mapping)
            if action_res not in action_tobe:
                action_tobe.append(action_res)
    return action_tobe


def generate_key(line):
    key=""
    text_match = re.search(r'>\s*([^<>]+)\s*<', line)
    alt_match = re.search(r'description="([^"]+)"', line)
    if text_match:
        key = text_match.group(1).strip()
    if len(key)<=1 and alt_match:
        key = alt_match.group(1).strip()
    if len(key)<=1:
        return "output error", "output error"
    input_text="output error"
    if line.startswith("input"):
        input_text=line.split(",")[-1].strip(")").strip()
    elif line.startswith("click"):
        input_text="click"
    elif line.startswith("scroll"):
        input_text="scroll"
    return key, input_text

#检验是否全是中文字符
def str_isall_chinese(str):
    for ch in str:
        if not u'\u4e00' <= ch <= u'\u9fa5':
            return False
    return True

#判断字符串是否包含中文
def str_contain_chinese(str):
    for ch in str:
        if u'\u4e00'<=ch<=u'\u9fff':
            return True
    return False


def sample_key(key_list,action_type_list,action_list):
    key="output error"
    action_type="output error"
    action="output error"

    inputList=[]
    clickList=[]
    otherList=[]
    for index in range(len(key_list)):
        if action_type_list[index]!="click":
            inputList.append(index)
        else:
            tempKey=key_list[index]
            if str_isall_chinese(tempKey)==True:
                clickList.append(index)
    if len(inputList)>0:
        index=random.randint(0,len(inputList)-1)
        i=inputList[index]
        key=key_list[i]
        action_type=action_type_list[i]
        action=action_list[i]
    elif len(clickList)>0:
        index=random.randint(0,len(clickList)-1)
        i=clickList[index]
        key=key_list[i]
        action_type=action_type_list[i]
        action=action_list[i]


    return key,action_type,action

# Define root directories
vis_root = "/zk/corpus/arm_01/"
pwd_root = "/home/corpus/arm_01"

# Define output directory and ensure it exists
output_root = "self_test/"
os.makedirs(output_root, mode=0o777, exist_ok=True)

# Initialize lists and dictionaries
data_json = []
testApp = ["Qunar", "duapp", "cloudweather", "pdfreader", "QQmail", "baicizhan", "zhuishushenqi", "QQmusic"]
trainAPP = ["ctrip", "gaodeMap", "didi", "pureweather", "vipshop", "xiaomiShop", "QQReader", "netmail", "youdao", "seekbooks", "kugou"]

# Additional counters and lists
count_temp = 0
count_long_html = 0
count_long_desc = 0
count_long_action = 0
count_none_action = 0
count_in_json1 = 0
count_in_json = 0
count_none = 0
count = 0
wrong_list = []

# Task-specific dictionaries
task1_dict = {}
task2_dict = {}
task3_dict = {}
task5_dict = {}

# List all directories in the root path
dirs = os.listdir(pwd_root)

# Set the maximum number of data points you want to generate
MAX_DATA_POINTS = 999999

for d in dirs:
    directory_path = os.path.join(vis_root, d) + "/"
    pwd_directory_path = os.path.join(pwd_root, d) + "/"
    
    # Check if the directory is in the test applications
    testFlag = any(d.startswith(app) for app in testApp)
    if not testFlag:
        continue
    
    # If the required JSON files exist, proceed
    if os.path.exists(pwd_directory_path + "data_all2unique.json"):
        data_all2unique = load_dict(pwd_directory_path + "data_all2unique.json")
        all_page_id = load_dict(pwd_directory_path + "all_page_id.json")
        all_action_id = load_dict(pwd_directory_path + "all_action_id.json")
        temp_data = {"page_name": "", "page_id": "", "node_name": "", "image": "", "path": []}
        
        print(d)
        print(len(data_all2unique))

        count_temp = 0
        dict_page_child = {}

        # Build the page hierarchy
        for page in all_page_id:
            if page not in dict_page_child:
                dict_page_child[page] = []
            levellist = page.split("_")[:]
            if len(levellist) > 1:
                page1 = "_".join(levellist[:-1])
                if page1 in dict_page_child:
                    if page not in dict_page_child[page1]:
                        dict_page_child[page1].append(page)
                else:
                    dict_page_child[page1] = [page]

        save_path_before = [page for page in dict_page_child if len(dict_page_child[page]) > 3]
        print("save_path_before", len(save_path_before))

        random.shuffle(save_path_before)

        # Limit the number of paths to process
        save_path_before = save_path_before[:MAX_DATA_POINTS]

        # Process each path before saving
        for path_before in save_path_before:
            path_after_list = dict_page_child[path_before]
            action_list = []
            action_type_list = []
            key_list = []

            # Skip small files
            if os.path.getsize(pwd_directory_path + path_before + "/" + path_before + "-screen.png") < 1024:
                continue
            if os.path.getsize(pwd_directory_path + path_before + "/" + path_before + "-html.txt") < 512:
                continue

            for path_after in path_after_list:
                levellist = path_after.split("_")[:]
                action_index = int(levellist[-1])
                action_res = get_action_by_id(all_action_id, action_index)
                
                key, action_type = generate_key(action_res)
                if "output error" in action_type or "scroll" in action_type:
                    continue
                
                action_list.append(action_res)
                key_list.append(key)
                action_type_list.append(action_type)

            if key_list:
                key, action_type, action = sample_key(key_list, action_type_list, action_list)
                if "output error" in action_type:
                    continue
                
                instruction = random.choice(click_instruction if action_type == "click" else input_instruction)
                res = instruction.format(text=key)

                with open(pwd_directory_path + path_before + "/" + path_before + "-html.txt", 'r', encoding='utf-8') as f:
                    html_after = f.read().strip()
                with open(pwd_directory_path + path_before + "/" + path_before + "-xml.txt", 'r', encoding='utf-8') as f:
                    xml_after = f.read().strip()

                icons_after, inputs_after, bounds_after, html2action_after = box_actions_generate(html_after, xml_after)
                action_dense = process_action(action, bounds_after, html2action_after)
                if isinstance(action_dense, str) and "error" not in action_dense:
                    data_line = [d, path_before, res, key, action_type, action_dense, action]
                    data_json.append(data_line)
                    if len(data_json) >= MAX_DATA_POINTS:
                        break

            if len(data_json) >= MAX_DATA_POINTS:
                break

    if len(data_json) >= MAX_DATA_POINTS:
        break
sample_size = 500
if len(data_json) > sample_size:
    data_json = random.sample(data_json, sample_size)
# Save the collected data to a JSON file
df = pd.DataFrame(data_json, columns=["APP", "path before", "path after", "key", "action_type", "action_dense", "action"])
df.to_json(os.path.join(output_root, "data_finetune.json"), orient="records", force_ascii=False, lines=True)



    
