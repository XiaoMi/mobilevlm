import os
import json
import pickle
import random
import time
import itertools

import jsonlines


from template.template_cn_multi import *
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

processed_data = []
#"Mobile-1M/Mobile-1M.jsonl"
#ann_path="Mobile-1M/Mobile-1M.jsonl"
vis_root="/zk/corpus/arm_01/"
pwd_root="/data/xwk/code/corpus/arm_01/"

#output_root="stage2/stage2_twoimg2action_0513/"#unique2all #multitask: only 11 train APP,  multitask_full_0501: all train APP
output_root="stage2/stage2_all_task1_0524/"
os.makedirs(output_root,mode=511,exist_ok=True)

data_json=[]
#temp_data={"page_name":"","page_id":"","node_name":"","image":"","path":[]}
#path_data={"name":"","name_id":"","html":"","image":"","action":"None","step":0}
testApp=["Qunar","duapp","cloudweather","pdfreader","QQmail","baicizhan","zhuishushenqi","QQmusic"]
trainAPP=["ctrip","gaodeMap","didi","pureweather","vipshop","xiaomiShop","QQReader","netmail","youdao","seekbooks","kugou"]

max_intput=0
max_output=0
count_temp=0

count_long_html=0
count_long_desc=0
count_long_action=0
count_none_action=0
#task4_dict={"ctrip_graph_8100" : [20883,{}]}

task4_dict={}
ctrip_path="/zk/corpus/arm_01/ctrip_graph_8100"
pwd_ctrip_path="/data/xwk/code/corpus/arm_01/ctrip_graph_8100"

dirs=os.listdir(pwd_root)


with open("testid/test_data.json", 'r', encoding='utf-8') as file:
    test_data = json.load(file)

count_in_json1=0
count_in_json=0
count_none=0
count=0
wrong_list=[]


task1_dict={}
task2_dict={}
task3_dict={}
task5_dict={}

for d in dirs:
    directory_path=vis_root+d+"/"
    pwd_directory_path=pwd_root+d+"/"
    testFlag=False
    trainFlag=False
    for testAppName in testApp: 
        if d.startswith(testAppName):
            testFlag=True
    if testFlag==True: continue  # 1 for training, 2 for validation, 3 for test
    
    #for trainAppName in trainAPP: 
    #    if d.startswith(trainAppName):
    #        trainFlag=True
    #if trainFlag==False: continue  # 1 for training, 2 for validation, 3 for test
    
    if os.path.exists(pwd_directory_path+"data_all2unique.json"):
        data_all2unique=load_dict(pwd_directory_path+"data_all2unique.json")#name [name,name_index]
        data_unique2all=load_dict(pwd_directory_path+"data_unique2all.json")
        all_page_id=load_dict(pwd_directory_path+"all_page_id.json") #page_name,page_id,
        all_action_id=load_dict(pwd_directory_path+"all_action_id.json")
        temp_data={"page_name":"","page_id":"","node_name":"","image":"","path":[]}
        print(d)
        print(len(data_unique2all))
        print(len(data_all2unique))

        count_temp=0

        #for page in data_all2unique:
        #for page in data_unique2all:
        for page in data_all2unique:
            count_temp+=1
            if count_temp%10000==0:
                print(count_temp)
                print(len(data_json))
            if count_temp<5:
                samp_data_json=data_json[-5:]
                for x in samp_data_json:
                    print("###############")
                    print(x["id"])
                    conver=x["conversations"]
                    for y in conver:
                        print(y["value"])
                print("!!!!!!!!!!!!!!!!")

            #if count_temp>200:
            #    continue
            complete_flag=True
            path_list=[]
            levellist=page.split("_")[:]

            if len(levellist)>1:
                page1="_".join(levellist[:-1])
                page2=page[:]
            else:
                page1=page[:]
                page2=page[:]
                #continue
            if page2 in test_data:
                continue
            if os.path.exists(pwd_directory_path+page+"/"+page1+"-html.txt") and os.path.exists(pwd_directory_path+page+"/"+page2+"-html.txt"):
                if os.path.exists(pwd_directory_path+page+"/"+page1+"-xml.txt") and os.path.exists(pwd_directory_path+page+"/"+page2+"-xml.txt"):

                    if os.path.getsize(pwd_directory_path+page+"/"+page1+"-screen.png")<1024:
                        continue
                    if os.path.getsize(pwd_directory_path+page+"/"+page2+"-screen.png")<1024:
                        continue
                    
                    with open(pwd_directory_path+page+"/"+page1+"-html.txt", 'r', encoding='utf-8') as f:
                        html_before=f.read().strip()  
                    with open(pwd_directory_path+page+"/"+page2+"-html.txt", 'r', encoding='utf-8') as f:
                        html_after=f.read().strip()  
                    #print(len(html_before))
                    #print(len(html_after))
                    if len(html_after)<200:
                        #print(page2)
                        continue
                    with open(pwd_directory_path+page+"/"+page1+"-xml.txt", 'r', encoding='utf-8') as f:
                        xml_before=f.read().strip()   
                    with open(pwd_directory_path+page+"/"+page2+"-xml.txt", 'r', encoding='utf-8') as f:
                        xml_after=f.read().strip()    
                    icons_before, inputs_before, bounds_before, html2action_before = box_actions_generate(html_before,xml_before)
                    #icons_after, inputs_after, bounds_after, html2action_after = box_actions_generate(html_after,xml_after)

                    #html_text_after=html2text(icons_after, inputs_after, bounds_after)
                    #if html_text_after =="html error":
                    #    continue

                    ######################################
                    
                    if len(levellist)<=1:
                        continue

                    task5_input = generate_task5_input()
                    conver=[]
                    value_user="Picture 1: <img>"+directory_path+page+"/"+page1+"-screen.png"+"</img>"+"\n"
                    value_user+="Picture 2: <img>"+directory_path+page+"/"+page2+"-screen.png"+"</img>"+"\n"
                    value_user+=task5_input
                    conver.append({"from":"user","value":value_user})

                    action_index=int(levellist[-1])
                    action_res=get_action_by_id(all_action_id,action_index)
                    action=process_action_box(action_res, bounds_before, html2action_before)


                    if action_res.startswith("input"):
                        count_in_json+=1
                    if isinstance(action, str) ==False or "error" in action:
                        if action_res.startswith("input"):
                            count_in_json1+=1
                            print("################################")
                            print("count_in_json",count_in_json)
                            print("count_in_json1",count_in_json1)
                        continue


                    if action =="input error" or action =="scroll error" or action =="click error":
                        continue

                    if isinstance(action, str)==False or action==None:
                        continue

                    if "img>" in action:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(id_)
                        print(action)
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        continue

                    conver.append({"from":"assistant","value":action})
                    
                    id_="task5_"+str(len(data_json))

                    data_json.append({"id":id_,"conversations":conver})

                    assert len(action)>1
                    if d not in task5_dict:
                        task5_dict[d]=[1,conver]
                    else:
                        task5_dict[d][0]+=1
                    

    with open(output_root+"task1"+"_stat.txt","w") as f:
        count_all=0
        for key in task1_dict:
            count_all+=task1_dict[key][0]
        f.write("total_num"+" : "+str(count_all)+"\n")
        
        for key in task1_dict:
            f.write(key+" : "+str(task1_dict[key][0])+"\n")

        for key in task1_dict:
            f.write("##########################")
            json.dump(task1_dict[key][1], f, indent=4,ensure_ascii=False)

    with open(output_root+"task2"+"_stat.txt","w") as f:
        count_all=0
        for key in task2_dict:
            count_all+=task2_dict[key][0]
        f.write("total_num"+" : "+str(count_all)+"\n")
        
        for key in task2_dict:
            f.write(key+" : "+str(task2_dict[key][0])+"\n")

        for key in task2_dict:
            f.write("##########################")
            json.dump(task2_dict[key][1], f, indent=4,ensure_ascii=False)

    with open(output_root+"task3"+"_stat.txt","w") as f:
        count_all=0
        for key in task3_dict:
            count_all+=task3_dict[key][0]
        f.write("total_num"+" : "+str(count_all)+"\n")
        
        for key in task3_dict:
            f.write(key+" : "+str(task3_dict[key][0])+"\n")

        for key in task3_dict:
            f.write("##########################")
            json.dump(task3_dict[key][1], f, indent=4,ensure_ascii=False)





    with open(output_root+"task4"+"_stat.txt","w") as f:
        for key in task4_dict:
            f.write(key+" : "+str(task4_dict[key][0])+"\n")

        for key in task4_dict:
            f.write("##########################")
            json.dump(task4_dict[key][1], f, indent=4,ensure_ascii=False)

    with open(output_root+"task5"+"_stat.txt","w") as f:
        count_all=0
        for key in task5_dict:
            count_all+=task5_dict[key][0]
        f.write("total_num"+" : "+str(count_all)+"\n")
        
        for key in task5_dict:
            f.write(key+" : "+str(task5_dict[key][0])+"\n")

        for key in task5_dict:
            f.write("##########################")
            json.dump(task5_dict[key][1], f, indent=4,ensure_ascii=False)





    with open(output_root+"data_multitask.json","w") as f:
        print(len(data_json))  
        json.dump(data_json, f, indent=4,ensure_ascii=False)
    #data_json=[]


