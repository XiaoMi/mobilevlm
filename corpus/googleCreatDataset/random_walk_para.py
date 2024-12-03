# coding: utf-8
#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
import argparse
import subprocess
import sys
import time
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
# from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from tqdm import tqdm
from agent_for_api.API_list import usr_api_list
from agent_for_api.agent_api_prompt import select_api_prompt, select_api_example
from agent_for_api.main_for_api import get_api_list
from agent_for_ui.agent_html_prompt import *
from selenium.common.exceptions import WebDriverException, InvalidElementStateException, NoSuchElementException
import json
from agent_for_ui.xml_to_html import any_tree_to_html
from chatgpt import chatgpt
import re
from app_list_MIUI import app_list
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import os
import random
import copy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
import PIL.Image

max_attempts = 5  # Set the maximum number of retry attempts


# currently tasks are all defined on single-app
'''
How does the entire demo work?
Use appium to obtain the xml information of the interface -> convert the local algorithm into html format -> 
package and send the task (task description + env_html) -> agent (planning + action) -> 
action is converted into appium's action and acts on the environment -> (task Description+env_html+action_history)->
The new action acts on the environment. (loop construction completed)
'''
# How to agent make decision?：
'''
planning action reward memory? 
'''

import xml.etree.ElementTree as ET
from anytree import Node
import numpy as np

import math
from collections import Counter


def parse_xml_to_anytree(xml_code):
    root = ET.fromstring(xml_code)

    def build_anytree(node, element, child_index, seen_elements, counter):
        element_type = element.tag
        # print(element_type)
        # Generate a unique key for the element based on its attributes
        element_key = (
            element_type,
            element.get('resource-id', ''),
            #  content-desc， text兼容问题
            element.get('content-desc', ''),
            element.get('text', ''),
            element.get('clickable', ''),
            element.get('scrollable', ''),
            element.get('package', ''),  ##
            element.get('class', ''),
            element.get('displayed', ''),
            element.get('bounds', ''),
        )
        seen_elements.add(element_key)

        # 检查是否有儿子节点
        is_leaf = not bool(list(element))

        # 检查 text 和 content-desc 是否至少有一个为真
        has_text = bool(element.get('text'))
        has_content_desc = bool(element.get('content-desc'))

        visible = has_text or has_content_desc or 'button' in element_type.lower() or 'edittext' in element.tag.lower()

        leaf_id = counter[0]  # 使用计数器作为 leaf_id
        counter[0] += 1  # 递增计数器

        anytree_node = Node(element_type, parent=node, type=element_type, visible=visible, leaf_id=leaf_id,
                            resource_id=element.get('resource-id'), content_desc=element.get('content-desc'),
                            text=element.get('text'), clickable=element.get('clickable'), is_leaf=is_leaf,
                            scrollable=element.get('scrollable'), package=element.get('package'),
                            class_label=element.get('class'), displayed=element.get('displayed'),
                            bounds=element.get('bounds'))

        for idx, child in enumerate(element):
            # print(idx)
            build_anytree(anytree_node, child, idx, seen_elements, counter)

    is_root_leaf = not bool(list(root))

    anytree_root = Node(root.tag, type=root.tag, visible=True, leaf_id=0,  # 初始计数器为 0
                        resource_id=root.get('resource-id'), content_desc=root.get('content-desc'),
                        text=root.get('text'), clickable=root.get('clickable'),
                        is_leaf=is_root_leaf, scrollable=root.get('scrollable'), package=root.get('package'),
                        class_label=root.get('class'), displayed=root.get('displayed'), bounds=root.get('bounds'))

    seen_elements = set()
    counter = [1]  # 使用列表来存储计数器的值，以便在递归中共享

    for idx, child in enumerate(root):
        # print("out",idx)
        build_anytree(anytree_root, child, idx, seen_elements, counter)

    return anytree_root



# actions define
def screen_click(element_id):
    element = driver.find_element(By.ID, element_id)  # use id to locate the element
    element.click()

def screen_text_input(element_id, input_text):
    element = driver.find_element(By.ID, element_id)  # use id to locate the element
    element.send_keys(input_text)

def screen_swipe(driver, start_x, start_y, end_x, end_y, duration=1000):
    # use duration to control the speed of swipe
    success = False
    while not success:
        try:
            driver.swipe(start_x, start_y, end_x, end_y, duration)
            success = True  # If the page source is acquired, set success to True to exit the loop
        except WebDriverException as e:
            print(f"Encountered an error: {e}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying




def get_memory(history_actions):
    memory_list = []
    # print(history_actions)
    for round_number, action_info in enumerate(history_actions, 1):
        key = None
        if 'action' in action_info:
            key = 'action'
            # round_number += 1  # 仅当键是 'action' 时增加 round_number
        elif 'thought' in action_info:
            key = 'thought'
        elif 'API call' in action_info:
            key = 'API call'
            # round_number += 1  # 仅当键是 'API call' 时增加 round_number
        else:
            key = 'unknown'
            # round_number += 1  # 对于其他未知类型也增加 round_number
        detail = action_info.get(key, 'No detail')
        # print(f"{key}: {detail}")
        memory_list.append(f"{action_info}")
        # memory_list.append(f"{key}: {detail}")

    if memory_list != []:
        # memory_list = memory_list[-10:]   # 记忆压缩。
        memory = "\n".join(memory_list)
    else:
        memory = "No action has been completed yet"
    return memory

def find_elements_by_criteria(driver, max_attempts=3, **criteria):
    selectors = []
    if 'id' in criteria:
        selectors.append(f'resourceId("{criteria["id"]}")')
    if 'text' in criteria:
        selectors.append(f'text("{criteria["text"]}")')
    if 'alt' in criteria:
        selectors.append(f'description("{criteria["alt"]}")')
    if 'class' in criteria:
        selectors.append(f'className("{criteria["class"]}")')

    if not selectors:
        print("没有定位到对应的元素")
        return None

    ui_selector = f'new UiSelector().' + '.'.join(selectors)
    attempt_count = 0
    while attempt_count < max_attempts:
        try:
            elements = driver.find_elements(MobileBy.ANDROID_UIAUTOMATOR, ui_selector)
            if len(elements) > 0:
                if len(elements) > 1:
                    print(f"警告: 存在多个具有相同属性的元素，这可能导致错误！")
                return elements
            attempt_count += 1
        except WebDriverException as e:
            print(f"遇到错误: {e}. 重试中...")
            time.sleep(5)
            attempt_count += 1

    print("服务器端错误或超过最大尝试次数")
    return None


def find_element(element, driver, max_attempts=3):
    id_match = re.search(r'id="([^"]+)"', element)
    text_match = re.search(r'>\s*([^<>]+)\s*<', element)
    alt_match = re.search(r'description="([^"]+)"', element)
    class_match = re.search(r'class="([^"]+)"', element)

    criteria = {}
    if id_match:
        criteria['id'] = id_match.group(1).strip()
    if text_match and not text_match.group(1).isspace():
        criteria['text'] = text_match.group(1).strip()
    if alt_match:
        criteria['alt'] = alt_match.group(1).strip()
    if class_match:
        criteria['class'] = class_match.group(1).strip()

    return find_elements_by_criteria(driver, max_attempts, **criteria)

def actions(res, history_actions, driver):
    if 'click(' in res:
        first_angle_bracket = res.find('<')
        first_reangle_bracket = res.find('>')
        second_angle_bracket = res.find('>', first_reangle_bracket + 1)
        # Extract the element from between these positions
        text = res[first_angle_bracket:second_angle_bracket + 1]
        list = find_element(text, driver)
        if list == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element click({text})"})
        elif len(list) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element click({text})"})
        else:
            try:
                list[0].click()
                history_actions.append({"Action": f"click({text})"})
            except WebDriverException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append({"Action": f"[Fail]: Unsuccessful click click({text})"})

    elif 'press(' in res:
        action = TouchAction(driver)
        first_angle_bracket = res.find('<')
        first_reangle_bracket = res.find('>')
        second_angle_bracket = res.find('>', first_reangle_bracket + 1)
        # Extract the element from between these positions
        text = res[first_angle_bracket:second_angle_bracket + 1]
        list = find_element(text, driver)
        if list == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element press({text})"})
        elif len(list) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element press({text})"})
        else:
            try:
                action.press(list[0]).wait(1000).release().perform()
                history_actions.append({"Action": f"press({text})"})
            except WebDriverException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append({"Action": f"[Fail]: Unsuccessful press({text})"})

    elif 'zoom(' in res:
        action1 = TouchAction(driver)
        action2 = TouchAction(driver)
        zoom_action = MultiAction(driver)
        first_angle_bracket = res.find('<')
        first_reangle_bracket = res.find('>')
        second_angle_bracket = res.find('>', first_reangle_bracket + 1)
        # Extract the element from between these positions
        text = res[first_angle_bracket:second_angle_bracket + 1]
        list = find_element(text, driver)
        if list == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element Zoom({text})"})
        elif len(list) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element Zoom({text})"})
        else:
            try:
                action1.press(list[0]).move_to(x=0, y=-100)  # 向上移动
                action2.press(list[0]).move_to(x=0, y=100)  # 向下移动
                zoom_action.add(action1, action2)
                zoom_action.perform()
                history_actions.append({"Action": f"Zoom({text})"})
            except WebDriverException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append({"Action": f"[Fail]: Unsuccessful zoom({text})"})

    elif 'pinch(' in res:
        action1 = TouchAction(driver)
        action2 = TouchAction(driver)

        first_angle_bracket = res.find('<')
        first_reangle_bracket = res.find('>')
        second_angle_bracket = res.find('>', first_reangle_bracket + 1)
        # Extract the element from between these positions
        text = res[first_angle_bracket:second_angle_bracket + 1]
        list = find_element(text, driver)
        if list == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element pinch({text})"})
        elif len(list) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element pinch({text})"})
        else:
            try:
                action1.press(x=list[0].location['x'], y=list[0].location['y'] - 100).move_to(list[0])
                action2.press(x=list[0].location['x'], y=list[0].location['y'] + 100).move_to(list[0])

                pinch_action = MultiAction(driver)
                pinch_action.add(action1, action2)
                pinch_action.perform()
                history_actions.append({"Action": f"pinch({text})"})
            except WebDriverException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append({"Action": f"[Fail]: Unsuccessful pinch({text})"})

    elif 'input(' in res:
        first_angle_bracket = res.find('<')
        first_reangle_bracket = res.find('>')
        second_angle_bracket = res.find('>', first_reangle_bracket + 1)
        # Extract the element from between these positions
        element = res[first_angle_bracket:second_angle_bracket + 1]
        input_context = res[second_angle_bracket + 2:-1].strip()
        input_context = input_context.strip('\'\"')
        # print(element)
        # print(input_context)
        list = find_element(element, driver)
        if list == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element. input({element}, {input_context})"})
        elif len(list) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element. input({element}, {input_context})"})
        else:
            try:
                # 点击元素
                list[0].click()
                history_actions.append({"Action": f"click({element})"})
                try:
                    WebDriverWait(driver, 1).until(
                        EC.staleness_of(list[0])
                    )
                    # 等待刷新

                except TimeoutException:
                    # 如果元素不存在或不可见，不执行input操作
                    list[0].send_keys(input_context)
                    history_actions.append({"Action": f"input({element}, {input_context})"})

            except InvalidElementStateException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append(
                    {"Action": f"[Fail]: InvalidElementStateException input({element}, {input_context})"})
            except NoSuchElementException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append({"Action": f"[Fail]: NoSuchElementException input({element}, {input_context})"})



    elif 'scroll(' in res or 'swipe(' in res:
        action = TouchAction(driver)

        numbers = re.findall(r'\d+', res)
        # 将找到的数字转换成整数并分配给相应的变量
        x1, y1, x2, y2 = map(int, numbers[:4])
        max_value = max(x1, y1, x2, y2)
        # 对滑动操作的参数进行调整，以免超出边界。
        if x1 == max_value:
            x1 -= 50
        if y1 == max_value:
            y1 -= 50
        if x2 == max_value:
            x2 -= 50
        if y2 == max_value:
            y2 -= 50

        # 如果某个数等于0，则加50
        if x1 == 0:
            x1 += 50
        if y1 == 0:
            y1 += 50
        if x2 == 0:
            x2 += 50
        if y2 == 0:
            y2 += 50
        success = False
        attempt_count = 0
        while not success and attempt_count < max_attempts:
            try:
                action.press(x=x1, y=y1).wait(ms=1000).move_to(x=x2, y=y2).release().perform()
                # driver.swipe(x1, y1, x2, y2, duration=1000) # swipe的效果不够好。
                success = True  # If the page source is acquired, set success to True to exit the loop
            except WebDriverException as e:
                attempt_count += 1
                print(f"Encountered an error: {e}. Retrying...")
                time.sleep(5)  # Wait for 5 seconds before retrying
        if success:
            history_actions.append({"Action": f"scroll([{x1},{y1}][{x2},{y2}])"})
        else:
            print("[Fail]: unsucess scroll.")
            history_actions.append({"Action": f"[Fail]: unsuccessful scroll scroll([{x1},{y1}][{x2},{y2}])"})

def get_page_source(driver):
    attempt_count = 0
    success = False
    xml_source = None
    while not success and attempt_count < max_attempts:
        try:
            xml_source = driver.page_source
            success = True  # If the page source is acquired, set success to True to exit the loop
        except WebDriverException as e:
            attempt_count += 1
            print(f"Encountered an error: {e}. Retrying...")
            time.sleep(3)  # Wait for 5 seconds before retrying
            # driver.quit()
            # driver = open_driver()
    return xml_source, driver


def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stderr = result.stderr
    
    if not stderr:
        return "API execution successful"
    else:
        print(stderr)
        return "API execution failed"

def api(res, history_actions):
    matches = re.findall(r'\[(.*)\]', res)
    success = False
    for match in matches:
        adb_command = match
        print("[API CALL]: ", adb_command)
        result = run_command(adb_command)
        print("[APi Function Call Result]: \033[34m" + result + "\033[0m")
        if 'success' in result:
            success = True
        # 有待商榷，执行失败的信息是否应该放在记录里，这样可以避免重复生成错误的API
        if "successful" in result:
            history_actions.append({f"API call": f"{adb_command}. [Call result]:{result}"})
        # history_actions.append({f"[API call]": f"{adb_command}. [Call result]:{result}"})
    return success


def get_success_memory(history_actions):
        memory_list = []
        counter = 0  # Initialize a counter
        for action_info in history_actions:
            key = None
            # 检查动作类型
            if 'action' in action_info or 'thought' in action_info:
                if 'action' in action_info:
                    key = 'action'
                elif 'thought' in action_info:
                    key = 'thought'

                # 当遇到 'action' 或 'thought' 时，每两次迭代增加一次计数
                if counter % 2 == 0:
                    round_number = counter // 2 + 1
                counter += 1

            elif 'API call' in action_info:
                key = 'API call'
                round_number = counter // 2 + 1  # 保持当前的 round_number

            elif 'App Select and Plan' in action_info:
                key = 'App Select and Plan'
                round_number = counter // 2 + 1  # 保持当前的 round_number

            else:
                key = 'unknown'
                round_number = counter // 2 + 1  # 保持当前的 round_number

            detail = action_info.get(key, 'No detail')
            memory_list.append(f"Step {round_number}: {key}: {detail}")

        memory = "\n".join(memory_list)
        return memory

def open_driver(command_executor, desired_caps):
    success = False
    attempt_count = 0
    while not success and attempt_count < max_attempts:
        try:
            driver = webdriver.Remote(command_executor, desired_caps)
            success = True
        except WebDriverException as e:
            attempt_count += 1
            print(f"Encountered an error: {e}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
    if not success:
        print(f"Failed to connect after {max_attempts} attempts. Exiting program.")
        driver.quit()
        sys.exit()  # Exit the program if connection is not successful
    else:
        print("[Device connected successfully!]")
        return driver

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extracting only id, app, packagename, query, and check_point information
    extracted_data = []
    for item in data:
        id = item.get('id')
        app = item.get('app')
        package_name = item['check_point'].get('package', [])
        query = item.get('query')
        check_point = item.get('check_point')
        extracted_data.append({
            'id': id,
            'app': app,
            'packagename': package_name,
            'query': query,
            'check_point': check_point
        })

    return extracted_data

def calculate_package_coverage(data_item, action_history):
    # 初始化覆盖数量
    coverage_count = 0
    if 'check_point' in data_item and 'package' in data_item['check_point']:
        package_names = data_item['check_point']['package']
        # 遍历 package_names 中的每个元素
        for package_name in package_names:
            # 检查元素是否出现在 action_history 的任何动作中
            if any(package_name in action for action in action_history):
                coverage_count += 1

        return coverage_count / len(package_names)
    else:
        return 0

def check_point_passed(check_point_value, action_history):
    if '|' in check_point_value:
        # 如果列表中有 '|', 那么任何一个 action_history 中的动作包含至少一个元素即通过
        return any(cp_elem in action for cp_elem in check_point_value if cp_elem != '|' for action in action_history), 1
    elif '&' in check_point_value:
        # 如果列表中有 '&', 那么 action_history 中的动作需要包含所有元素
        return all(cp_elem in action for cp_elem in check_point_value if cp_elem != '&' for action in action_history), 1
    else:
        if isinstance(check_point_value, list):
            total_elems = len(check_point_value)
            passed_elems = sum(any(cp_elem in action for action in action_history) for cp_elem in check_point_value)
            return passed_elems, total_elems
        else:
            return any(check_point_value in action for action in action_history), 1

# check point scores
def check_points(data_item, action_history):
    checkpoints = ['activity', 'resource-id', 'text', 'package', 'api']
    total_checkpoints = 0
    passed_checkpoints = 0

    for cp in checkpoints:
        if cp in data_item['check_point'] and data_item['check_point'][cp]:   # check existence
            check_point_value = data_item['check_point'][cp]
            if isinstance(check_point_value, list):
                passed, total = check_point_passed(check_point_value, action_history)
                passed_checkpoints += passed
                total_checkpoints += total
            else:
                # 直接比较
                total_checkpoints += 1
                if any(check_point_value in action for action in action_history):
                    passed_checkpoints += 1

    return passed_checkpoints / total_checkpoints if total_checkpoints > 0 else 0

def format_api_info_as_text(text, data):
    """
    Format the API information as text in the specified format if the name_ch or name_en of an app is found in the text.
    :param text: The string in which to search for app names.
    :param data: The JSON data containing app information.
    :return: A string formatted as a dictionary with app names as keys and their API information as values.
    """
    formatted_info = {}
    general_keys_api = [
        {
            "ADB Command": "adb shell input keyevent KEYCODE_BACK",
            "Function Description": "Return to previous page",
            "Parameter Information": "No additional parameters required."
        },
        {
            "ADB Command": "adb shell input keyevent KEYCODE_HOME",
            "Function Description": "go to home page, which is equal to click the home button",
            "Parameter Information": "No additional parameters required."
        },
        {
            "ADB Command": "adb shell input keyevent KEYCODE_SLEEP",
            "Function Description": "Set the device to sleep",
            "Parameter Information": "No additional parameters required."
        },
        {
            "ADB Command": "adb shell screencap -p /sdcard/screenshot.png",
            "Function Description": "Takes a screenshot and saves it.",
            "Parameter Information": "No additional parameters required."
        },
        {
            "ADB Command": "adb shell input keyevent KEYCODE_WAKEUP",
            "Function Description": "Wake up the device",
            "Parameter Information": "No additional parameters required."
        }
    ]
    formatted_info["通用按键"] = general_keys_api

    for app in data:
        #if re.search(r'\b' + re.escape(app['name_ch']) + r'\b', text) or re.search(
        #        r'\b' + re.escape(app['name_en']) + r'\b', text):
        if app['name_en'] in text or app['name_ch'] in text:
            api_info = app['api']
            if api_info:
                formatted_info[app['name_ch']] = api_info

    # Convert the dictionary to a string formatted as a dictionary
    formatted_text = json.dumps(formatted_info, indent=2, ensure_ascii=False)
    return formatted_text


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
def calculate_scroll_parameters(window_size, html, direction, scroll_type):
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

def process_user_input(window_size, user_input, elements_map):  # 将用户的输入转化为实际的执行指令
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
            params_command = calculate_scroll_parameters(window_size, html_element, direction, scroll_type)
    elif action == 'input':
        action_command = 'input'
        if params and params[0].isdigit() and int(params[0]) in elements_map:
            params_command = elements_map[int(params[0])]
            if len(params) > 1:
                params_command += f", '{params[1]}'"

    # Construct the final command
    final_command = f"{action_command}({params_command})"

    return final_command

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
                    print(f"{index:{max_index_length}}: {description}")

                    action_space[index]=category_name
    return action_space

def gen_action_list(action_space,window_size):
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
            random.shuffle(current_text_list)
            action_res="input("+str(index)+","+current_text_list[0]+")"
            action_list.append(action_res)

        #window_size = driver.get_window_size()
        for action_res in action_list:
            action_res = process_user_input(window_size, action_res, mapping)
            if action_res not in action_tobe:
                action_tobe.append(action_res)
    return action_tobe
def compare_html_acc(html_code_save,html_code):
    html_code_save_list=html_code_save.strip().split("\n")
    html_code_list=html_code.strip().split("\n")
    index=0
    correct=[]
    for code_ in html_code_list:
        if code_ in html_code_save_list:
            index+=1
            correct.append(1)
        else:
            correct.append(0)
    #if float(index)/len(html_code_list)<0.9:
    #    print("###############html_code_save##############")
    #    print(html_code_save)
    #    print("###############html_code##############")
    #    print(html_code)
    #    print(correct)
    return float(index)/len(html_code_list), index, len(html_code_list),float(index)/len(html_code_save_list)

def restart_from_homepage(start_APP_command,history_list,driver,deviceName,waitadb):
    history_actions=[]
    for i in range(len(start_APP_command)):
        temp_command=start_APP_command[i]
        if "adb shell" in temp_command:
            temp_command=set_adb(temp_command,deviceName)
        result = api(temp_command, history_actions)
        if "adb" in temp_command.lower():
            if len(start_APP_command)>1 and i==0:
                time.sleep(5)
            else:
                time.sleep(waitadb)
        else:
            time.sleep(3)
    print("restart")
    print(temp_command)

    history_actions=[]
    for temp_command in history_list:

        if "adb shell" in temp_command:
            temp_command=set_adb(temp_command,deviceName)
        actions(temp_command, history_actions, driver)
        print(temp_command)
        if "adb" in temp_command.lower():
            time.sleep(waitadb)
        else:
            time.sleep(3)
    return history_actions

def get_filelist(dir, Filelist):
    newDir = dir
    if os.path.isfile(dir):
        Filelist.append(dir)
        # # 若只是要返回文件文，使用这个
        # Filelist.append(os.path.basename(dir))
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            # 如果需要忽略某些文件夹，使用以下代码
            #if s == "xxx":
                #continue
            newDir=os.path.join(dir,s)
            get_filelist(newDir, Filelist)
    return Filelist

def click_cancel(driver):
    #cancel_button = driver.find_element_by_id("com.miui.systemAdSolution:id/cancel_dialog")
    #if cancel_button:
    #    cancel_button.click()
    cancel_button = driver.find_elements(MobileBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("取消")')
    if cancel_button:
        cancel_button[0].click()

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


def get_parser():
    parser = argparse.ArgumentParser(description="Agent for mobile phone")
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature')
    parser.add_argument('--model', type=str, default='gpt-4', help='model to use')
    parser.add_argument('--dataset', type=str, default='data/s_app_m_step_utf8.json', help='dataset to use')
    parser.add_argument('--max_steps', type=int, choices=range(0, 50), default=20, help='numbers of steps')
    parser.add_argument('--start_index', type=int, default=0, help='start_index')
    parser.add_argument('--device_name', type=str, default='0.0.0.0:6520', help='device to use')
    parser.add_argument('--systemPort', type=int, default=8201, help='appium client port')
    parser.add_argument('--command_executor', type=str, default='http://127.0.0.1:4800/wd/hub',
                        help='appium server port')
    parser.add_argument('--appPackage', type=str, default='ctrip.android.view',
                        help='which app to randomly walk')
    parser.add_argument('--name_en', type=str, default='ctrip')
    parser.add_argument('--diff_max', type=float, default=0.5)
    parser.add_argument('--diff_png', type=float, default=0.3)
    parser.add_argument('--waitadb', type=int, default=5)
    return parser

def set_adb(command,deviceName):
    if "adb shell" in command:
        new_adb="adb -s "+deviceName+" shell"
        command=command.replace("adb shell", new_adb)
    return command

def find_index(path,name):
    index=0
    dirs = os.listdir(path)
    for temp_p in dirs:
        if temp_p.startswith(name) and len(temp_p)>len(name)+1 and temp_p.endswith("-html.txt"):
            #print(temp_p)
            temp_index=temp_p[len(name)+1:].split("-")[0]
            if len(temp_index)>0:
                if temp_index[0]>="0" and temp_index[0]<="9":
                    temp_index=int(temp_index)
                    if temp_index>index:
                        index=temp_index
    return index+1


def find_last(path,name):
    index=0
    last_name=name[:]
    dirs = os.listdir(path)
    for temp_p in dirs:
        if temp_p.startswith(name) and len(temp_p)>len(name)+1 and temp_p.endswith("-html.txt"):
            #print(temp_p)
            temp_index=temp_p[len(name)+1:].split("-")[0]
            if len(temp_index)>0:
                if temp_index[0]>="0" and temp_index[0]<="9":
                    print(temp_p)
                    temp_index=int(temp_index)
                    if temp_index>index:
                        index=temp_index
                        last_name=temp_p.split("-html")[0]
    return last_name


class BM25:
    def __init__(self, docs,docs_names, k1=1.5, b=0.75):
        """
        BM25算法的构造器
        :param docs: 分词后的文档列表，每个文档是一个包含词汇的列表
        :param k1: BM25算法中的调节参数k1
        :param b: BM25算法中的调节参数b
        """
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.doc_len = [len(doc) for doc in docs]  # 计算每个文档的长度
        self.avgdl = sum(self.doc_len) / len(docs)  # 计算所有文档的平均长度
        self.doc_freqs = []  # 存储每个文档的词频
        self.idf = {}  # 存储每个词的逆文档频率
        self.df={}
        self.initialize()
        self.doc_names=docs_names

    def initialize(self):
        """
        初始化方法，计算所有词的逆文档频率
        """
        #df = {}  # 用于存储每个词在多少不同文档中出现
        for doc in self.docs:
            # 为每个文档创建一个词频统计
            self.doc_freqs.append(Counter(doc))
            # 更新df值
            for word in set(doc):
                self.df[word] = self.df.get(word, 0) + 1
        # 计算每个词的IDF值
        for word, freq in self.df.items():
            self.idf[word] = math.log((len(self.docs) - freq + 0.5) / (freq + 0.5) + 1)

    def appendItem(self, doc,doc_name):
        if doc_name not in self.doc_names:
            for word in set(doc):
                self.df[word] = self.df.get(word, 0) + 1
            # 计算每个词的IDF值
            for word in set(doc):
                freq=self.df[word]
                self.idf[word] = math.log((len(self.docs) - freq + 0.5) / (freq + 0.5) + 1)
            #max_len=len(self.doc_names)
            self.doc_names.append(doc_name)

    def score(self, doc, query):
        """
        计算文档与查询的BM25得分
        :param doc: 文档的索引
        :param query: 查询词列表
        :return: 该文档与查询的相关性得分
        """
        score = 0.0
        for word in query:
            if word in self.doc_freqs[doc]:
                freq = self.doc_freqs[doc][word]  # 词在文档中的频率
                # 应用BM25计算公式
                score += (self.idf[word] * freq * (self.k1 + 1)) / (freq + self.k1 * (1 - self.b + self.b * self.doc_len[doc] / self.avgdl))
        return score

    def get_max(self,query):
        scores = [self.score(i, query) for i in range(len(self.docs))]
        index=np.argmax(scores)
        return index,self.doc_names[index]


def compare_nodes(node1, node2, current_depth, max_depths, differences, total_nodes):
    """递归比较两个节点及其子节点的结构差异，并更新最大深度和差异数。"""
    # 更新最大深度
    max_depths[0] = max(max_depths[0], current_depth)

    # 如果其中一个节点为 None，则计算另一个节点及其所有子节点的数量作为差异
    if node1 is None or node2 is None:
        non_none_node = node1 if node1 is not None else node2
        differences[0] += count_all_nodes(non_none_node)
        return

    # 对子节点进行递归比较
    children1 = list(node1)
    children2 = list(node2)
    max_len = max(len(children1), len(children2))

    for i in range(max_len):
        child1 = children1[i] if i < len(children1) else None
        child2 = children2[i] if i < len(children2) else None
        compare_nodes(child1, child2, current_depth + 1, max_depths, differences, total_nodes)

def count_nodes(node, current_depth, max_depths):
    """
    计算给定节点及其所有子节点的总数，并更新最大深度。
    """
    if node is None:
        return 0
    else:
        # 更新最大深度
        max_depths[0] = max(max_depths[0], current_depth)
        count = 1  # 当前节点
        for child in list(node):
            count += count_nodes(child, current_depth + 1, max_depths)  # 递归计算子节点
        return count


def calculate_max_depth(node, current_depth=1):
    if node is None:
        return current_depth
    max_depth = current_depth
    for child in list(node):
        child_depth = calculate_max_depth(child, current_depth + 1)
        max_depth = max(max_depth, child_depth)
    return max_depth


def count_all_nodes(node):
    """递归计算一个节点下所有子节点的数量，包括自身。"""
    return 1 + sum(count_all_nodes(child) for child in list(node))


def compare_xml(xml1, xml2, difference_limit):
    root1 = ET.fromstring(xml1)
    root2 = ET.fromstring(xml2)

    total_nodes1 = count_all_nodes(root1)
    total_nodes2 = count_all_nodes(root2)
    total_nodes_avg = (total_nodes1 + total_nodes2) / 2

    # 计算深度差值
    differences = [0]  # 用于记录结构差异的总数
    max_depths = [0]  # 用于记录遍历到的最大深度
    compare_nodes(root1, root2, 1, max_depths, differences, total_nodes_avg)
    normalized_difference = differences[0] / total_nodes_avg
    print("Normalized structural difference:", normalized_difference)
    print("Maximum depth reached:", max_depths[0])
    return normalized_difference < difference_limit , normalized_difference



def compare_images(img_path1, img_path2, threshold):
    """
    Compare two images and determine if they are the same based on pixel values.

    :param img_path1: Path to the first image.
    :param img_path2: Path to the second image.
    :param threshold: The threshold for considering the images as the different.

    :return: True if the images are the same based on the given threshold, False otherwise.
    """
    # Open the images
    try:
        img1 = PIL.Image.open(img_path1)
        img2 = PIL.Image.open(img_path2)
    except IOError:
        print("Error in opening one of the images.")
        return False

    # Convert images to numpy arrays
    img1_array = np.array(img1)
    img2_array = np.array(img2)

    # Check if dimensions are the same
    if img1_array.shape != img2_array.shape:
        print("Images have different dimensions.")
        return False

    # Calculate the number of equal pixels
    equal_pixels = np.sum(img1_array == img2_array)

    # Total number of pixels
    total_pixels = img1_array.size

    # Calculate the ratio of equal pixels
    similarity_ratio = equal_pixels / total_pixels
    dif_ratio = 1 - similarity_ratio
    print("dif_ratio: ", dif_ratio)
    return dif_ratio < threshold, dif_ratio



def compare_image_and_xml(xml_path_1, xml_path_2, threshold_xml, screenshot_filepath_1, screenshot_filepath_2, threshold_image):
    with open(xml_path_1, 'r', encoding='utf-8') as html_file:
        xml_1 = html_file.read()
    with open(xml_path_2, 'r', encoding='utf-8') as html_file:
        xml_2 = html_file.read()
    result_xml, result_nums = compare_xml(xml_1, xml_2, threshold_xml)
    result_images, result_difs = compare_images(screenshot_filepath_1, screenshot_filepath_2, threshold_image)
    return result_xml,result_images, result_nums, result_difs

parser = get_parser()
args = parser.parse_args()
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    t = time.localtime()
    model_name = args.model.replace('/', '-')

    # read data
    with open("corpus/human_anno_data_tobe.json", 'r') as file:
        data = json.load(file)
    human_anno_data_done=[]

    if os.path.exists("corpus/human_anno_data_tobe.json"):
        with open("corpus/human_anno_data_tobe.json", 'r') as file:
            human_anno_data_done = json.load(file)
    #data = read_json_file("corpus/instruct_data_APP2query2id.json")
    # read APP list
    with open('app_list_MIUI.json', 'r', encoding='utf-8') as file:
        all_app_list = json.load(file)

    app_name_en_data={}
    app_package_data={}
    for index in range(len(all_app_list)):
        item=all_app_list[index]
        item["app_id"]=index
        if "name_en" in item:
            app_name_en_data[item["name_en"]]=item
        else:
            print(item)
        if "package" in item:
            app_package_data[item["package"]]=item
        else:
            print(item)


    print("***[TEST BEGIN]***")
    print("total_data_num: ",len(data))
    print("total_app_num: ",len(all_app_list))

    cnt = 0
    total_steps = 0
    pass_cnt = 0
    check_result_1 = 0
    check_result_2 = 0


    start_index = args.start_index  # Change this to the index you want to start testing from
    '''
    appPackage = "ctrip.android.view"
    appPackage1="com.ss.android.ugc.aweme"
    appActivity = ".activity.MainTabActivity"
    desired_caps = {
        "platformName": "Android",  # 操作系统
        "deviceName": "10.13.2.29:6529",
        "platformVersion": "13",
        'automationName': 'uiautomator2',
        'noReset': True,
        # 'unicodeKeyboard': True,
        # 'resetKeyboard': False,
        "newCommandTimeout": 6000,
        "uiautomator2ServerLaunchTimeout": 60000,
        # 'skipServerInstallation': 'false',
    }
    '''
    appPackage = args.appPackage
    device_name = args.device_name
    systemPort = args.systemPort
    command_executor=args.command_executor
    waitadb=args.waitadb
    desired_caps = {
        "platformName": "Android",
        "deviceName": device_name,
        "udid": device_name,
        "platformVersion": "13.0",
        'automationName': 'uiautomator2',
        'noReset': True,
        # 'unicodeKeyboard': True,
        # 'resetKeyboard': False,
        'newCommandTimeout': 6000,
        'uiautomator2ServerLaunchTimeout': 60000,
        # 'skipServerInstallation': 'false',
        'systemPort': systemPort
    }
    print("[start connected]")
    # driver to connect to the emulator
    driver = open_driver(command_executor, desired_caps)


    print( driver.get_window_size())#{'width': 720, 'height': 1184}


    #input("get_window_size")
    

    #current_APP=["ctrip"]
    #current_adb=["[adb shell am start -n ctrip.android.view/ctrip.business.splash.CtripSplashActivity]"]
    #current_text_list=["北京市","上海市","合肥市","海南市","天津市","哈尔滨市","三亚","乌鲁木齐"]

    app_parameters=load_json("app_parameters"+".json")
    #app_parameters={"data":[]}
    #temp_json={"name_en":current_APP[0],"adb":current_adb,"text":current_text_list}
    #app_parameters["data"].append(temp_json)
    #save_json("app_parameters"+".json",app_parameters)

    temp_flag=0
    name_en=args.name_en
    for temp_json in app_parameters["data"]:
        if temp_json["name_en"]==name_en:
            current_adb=temp_json["adb"]
            current_text_list=temp_json["text"]
            temp_flag=1
            break
    #if temp_flag==0:
    #    input("wrong APP name")

    if name_en in app_package_data:
        name_ch=app_name_en_data[name_en]["name_ch"]
    else:
        name_ch=name_en
    data_output_path="corpus/random_walk/"+name_en+"_graph_"+str(systemPort)+"/"

    os.makedirs(data_output_path,mode=511,exist_ok=True)
    round_number=1
    if not os.path.exists(data_output_path+name_en+"0.json"):
        close_webview_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "org.chromium.webview_shell"]
        subprocess.run(close_webview_command)
        close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
        subprocess.run(close_gallery_command)

        close_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", appPackage]
        subprocess.run(close_command)
        #click_cancel(driver)

        curr_path=name_en+"0"
        start_APP_command=current_adb
        history_actions=[]
        for temp_command in start_APP_command:
            if "adb shell" in temp_command:
                temp_command=set_adb(temp_command,device_name)
            result = api(temp_command, history_actions)
            if "adb" in temp_command.lower():
                time.sleep(waitadb)
            else:
                time.sleep(2)
        xml_source, driver = get_page_source(driver)
        if xml_source == None:
            xml_source, driver = get_page_source(driver)
        xml_code=xml_source[:]
        #print(xml_source)
        anytree_root = parse_xml_to_anytree(xml_source)
        # translate xml to html
        html_code = any_tree_to_html(anytree_root, 0, None)

        mapping = map_and_reverse_complete_interactive_elements(html_code)
        action_space = display_html_and_mapping(html_code, mapping)

        window_size = driver.get_window_size()
        action_list= gen_action_list(action_space,window_size)


        screencap_command = f"adb -s {device_name} shell screencap -p >"+data_output_path+curr_path+"-screen.png"
        subprocess.run(screencap_command,shell=True)

        save_txt(data_output_path+curr_path+"-html.txt",html_code)
        save_txt(data_output_path+curr_path+"-xml.txt",xml_code)
        data_json_before={"round":round_number, "name":curr_path,"unique_name":curr_path,"valid":True,\
            "start_APP":start_APP_command,"history_actions":[],\
            "action_valid":[], "action_invalid":[],"action_name_list":[],"parent":""}
        save_json(data_output_path+curr_path+".json",data_json_before)
        all_unique_page={"num":0, "data":[],"need":[]}
        all_unique_page["data"].append({"round":round_number,"name":curr_path,"name_id":0,"history_actions":[],"num_actions":0,"failed":0})
        all_unique_page["need"].append([len(all_unique_page["data"])-1,round_number])
        all_unique_page["num"]=len(all_unique_page["data"])
        save_json(data_output_path+"all_unique_page.json",all_unique_page)
        all_triple={"num":0,"data":[]}
        all_page_id={}
        all_page_id[curr_path]=0
        all_action_id={}
        save_json(data_output_path+"all_triple.json",all_triple)
        save_dict(data_output_path+"all_page_id.json",all_page_id)
        save_dict(data_output_path+"all_action_id.json",all_action_id)

        data_unique2all={}
        data_unique2all[curr_path]=[curr_path]
        data_all2unique={}
        data_all2unique[curr_path]=curr_path
        data_unique2action={}
        data_unique2action[curr_path]=[]
        save_dict(data_output_path+"data_unique2all.json",data_unique2all)
        save_dict(data_output_path+"data_all2unique.json",data_all2unique)
        save_dict(data_output_path+"data_unique2action.json",data_unique2action)



    task_continue=True
    max_steps=7
    
    close_webview_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "org.chromium.webview_shell"]
    subprocess.run(close_webview_command)
    close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
    subprocess.run(close_gallery_command)

    close_command = ["adb","-s", device_name , "shell", "am", "force-stop", appPackage]
    history_actions=[]
    subprocess.run(close_command)


    all_unique_page=load_json(data_output_path+"all_unique_page.json")
    #data {round,page_name,page_id,history_actions,num_actions,num_pages,done}
    #need [data_index,data_round]

    data_unique2all=load_dict(data_output_path+"data_unique2all.json")#name, name
    data_all2unique=load_dict(data_output_path+"data_all2unique.json")#name [name,name_index]
    data_unique2action=load_dict(data_output_path+"data_unique2action.json")#name, [action1,action2]

    all_triple=load_json(data_output_path+"all_triple.json") #data:[page1,action,page2] page_id, action_id, page_id
    all_page_id=load_dict(data_output_path+"all_page_id.json") #page_name,page_id,
    all_action_id=load_dict(data_output_path+"all_action_id.json")#action_name, action_id

    docs=[]
    docs_names=[]
    index=0
    for key in data_unique2all:
        level_path="/".join(key.split("_")[:-1])+"/"
        with open(data_output_path+level_path+key+"-html.txt", 'r', encoding='utf-8') as f:
            html_code_save=f.readlines()
            #print(len(html_code_save))
            docs.append(html_code_save)
        docs_names.append(key)
        #index+=1

    # 初始化BM25模型并计算得分
    bm25 = BM25(docs,docs_names)

    start_point=["0_1c","0_32c","0_33c","0_34c"]#设置、搜索、我的#


    key_max_step=5

    all_data_index=0
    count_before_cycle=0
    while len(all_unique_page["need"])>0:
        random_index=0
        if all_unique_page["need"][random_index][1]>2:
            random_index=random.randint(0,len(all_unique_page["need"])-1)
        if all_unique_page["need"][random_index][1]>max_steps:
            max_len=len(all_unique_page["need"])
            temp_flag=0
            new_index=all_data_index
            for i in range(max_len):
                new_index=(i+all_data_index)%max_len
                if all_unique_page["need"][new_index][1]<=max_steps:
                    temp_flag=1
                    break
            if temp_flag==0:
                break
            random_index=new_index

        all_data_index=all_unique_page["need"][random_index][0]

        before_data_key=all_unique_page["data"][all_data_index]
        name_before=all_unique_page["data"][all_data_index]["name"]

        
        level_path="/".join(name_before.split("_")[:-1])+"/"
        os.makedirs(data_output_path+level_path,mode=511,exist_ok=True)
        with open(data_output_path+level_path+name_before+".json", 'r', encoding='utf-8') as file:
            data_json_before = json.load(file)

        #html_code_save=[]
        with open(data_output_path+level_path+name_before+"-html.txt", 'r', encoding='utf-8') as f:
            html_code_save=f.read()
        #xml_code_save=[]
        with open(data_output_path+level_path+name_before+"-xml.txt", 'r', encoding='utf-8') as f:
            xml_code_save=f.read()

        mapping = map_and_reverse_complete_interactive_elements(html_code_save)
        action_space=display_html_and_mapping(html_code_save, mapping)

        window_size = driver.get_window_size()
        action_list_save = gen_action_list(action_space,window_size)



        close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
        subprocess.run(close_gallery_command)

        close_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", appPackage]
        subprocess.run(close_command)
        #click_cancel(driver)

        start_APP_command=data_json_before["start_APP"]
        history_list=data_json_before["history_actions"]
        round_number=data_json_before["round"]
        #print("history_list",history_list)


        temp_actions=restart_from_homepage(start_APP_command,history_list,driver,device_name,waitadb)

        if  all_unique_page["data"][all_data_index]["failed"]>=3:
            all_unique_page["need"].pop(random_index)
            continue

        fail_flag=True
        print("#################")
        print(temp_actions)
        print("#################")
        for temp_action in temp_actions: # cannot restart
            if "[Fail]:" in temp_action["Action"]:
                print("has wrong command")
                all_unique_page["data"][all_data_index]["failed"]+=1
                fail_flag=False
                break
        if fail_flag==False:
            continue


        #name_before_last=find_last(data_output_path+level_path,name_before)

        xml_source, driver = get_page_source(driver) 
        if xml_source == None:
            all_unique_page["data"][all_data_index]["failed"]+=1
            continue
        xml_code_before=xml_source[:]
        anytree_root = parse_xml_to_anytree(xml_source)
        html_code_before = any_tree_to_html(anytree_root, 0, None)

        diff_max=args.diff_max
        #if len(html_code_before)>20:
        #    diff_max+=(len(html_code_before)-10)//10


        result_xml, result_nums = compare_xml(xml_code_before, xml_code_save, diff_max)

        mapping = map_and_reverse_complete_interactive_elements(html_code_before)
        action_space=display_html_and_mapping(html_code_before, mapping)

        window_size = driver.get_window_size()
        action_list = gen_action_list(action_space,window_size)

        if result_xml==False: # restart, not same xml
            print(name_before)
            print(diff_max)
            #input("result_xml= False")
            new_index=find_index(data_output_path+level_path,name_before)
            #if new_index>0:
            new_name_before=name_before+"-"+str(new_index)

            level_path="/".join(new_name_before.split("_")[:-1])+"/"
            os.makedirs(data_output_path+level_path,mode=511,exist_ok=True)

            screencap_command = f"adb -s {device_name} shell screencap -p >"+data_output_path+level_path+new_name_before+"-screen.png"
            subprocess.run(screencap_command,shell=True)

            save_txt(data_output_path+level_path+new_name_before+"-html.txt",html_code_before)
            save_txt(data_output_path+level_path+new_name_before+"-xml.txt",xml_code_before)

            if new_name_before not in all_page_id:
                page_id=len(all_page_id)
                all_page_id[new_name_before]=page_id
                save_dict(data_output_path+"all_page_id.json",all_page_id)

            temp_flag=0
            if new_name_before not in data_all2unique:

                diff_max=args.diff_max
                diff_png=args.diff_png
                with open(data_output_path+level_path+new_name_before+"-html.txt", 'r', encoding='utf-8') as f:
                    bm_query=f.readlines()
                    f.close()
                compare_index,compare_name=bm25.get_max(bm_query)
                print(compare_name)
                #input("Enter:")
                #for compare_name in data_unique2all:
                level_compare_path="/".join(compare_name.split("_")[:-1])+"/"
                result_xml,result_images, result_nums, result_difs=compare_image_and_xml(
                    data_output_path+level_path+new_name_before+"-xml.txt", 
                    data_output_path+level_compare_path+compare_name+"-xml.txt", diff_max, 
                    data_output_path+level_path+new_name_before+"-screen.png", 
                    data_output_path+level_compare_path+compare_name+"-screen.png", diff_png)
                if result_xml==True and result_images==True:
                    if new_name_before not in data_unique2all[compare_name]:
                        data_unique2all[compare_name].append(new_name_before)
                    data_all2unique[new_name_before]=compare_name
                    temp_flag=1
                    #break
                if temp_flag==0:
                    data_unique2all[new_name_before]=[new_name_before]
                    data_all2unique[new_name_before]=new_name_before
                    all_unique_page["data"].append({"round":round_number,"name":new_name_before,"name_id":all_page_id[new_name_before],
                        "history_actions":[],"num_actions":0,"failed":0})
                    all_unique_page["need"].append([len(all_unique_page["data"])-1,round_number])
                    all_unique_page["num"]=len(all_unique_page["data"])
                    if new_name_before not in data_unique2action:
                        data_unique2action[new_name_before]=[]
                    bm25.appendItem(bm_query,new_name_before)
        
                    save_dict(data_output_path+"data_unique2all.json",data_unique2all)
                    save_dict(data_output_path+"data_all2unique.json",data_all2unique)
                    save_dict(data_output_path+"data_unique2action.json",data_unique2action)


            data_json_before={"round":round_number, "name":new_name_before,"unique_name":data_all2unique[new_name_before],"valid":True,\
                "start_APP":start_APP_command,"history_actions":history_list,\
                "action_valid":[], "action_invalid":[],"action_name_list":[],"parent":data_json_before["parent"]}

            save_json(data_output_path+level_path+new_name_before+".json",data_json_before)

            all_unique_page["data"][all_data_index]["failed"]+=1
            continue

        count_cycle=0
        action_flag=0
        for action_res in action_list:
            if action_res not in action_list_save: #保证每个指令都是第一次保存过，并且这次也出现了。像是广告指令就放弃吧
                continue 
            action_name_list =data_json_before["action_name_list"]
            unique_before_action_list=data_unique2action[name_before]
            if action_res in action_name_list or action_res in unique_before_action_list:
                continue

            if action_res not in all_action_id:
                action_index=len(all_action_id)
                all_action_id[action_res]=action_index
                save_dict(data_output_path+"all_action_id.json",all_action_id)
            action_index=all_action_id[action_res]

            name_after=name_before+"_"+str(action_index)
            level_path_after="/".join(name_after.split("_")[:-1])+"/"
            

            if os.path.exists(data_output_path+level_path_after+name_after+".json"):
                data_json_before["action_name_list"].append(action_res)
                continue
                    

            history_list=data_json_before["history_actions"]
            history_actions=["None"]
            actions(action_res,history_actions, driver)
            time.sleep(3)

            last_action_result=history_actions[-1]["Action"]


            xml_source, driver = get_page_source(driver)
            if xml_source == None:
                time.sleep(3)
                xml_source, driver = get_page_source(driver)

            if "[Fail]:" in last_action_result or xml_source==None:
                data_json_before["action_name_list"].append(action_res)
                temp_action_valid={"action_id":action_index,"action":action_res,"action_res":last_action_result}
                data_json_before["action_invalid"].append(temp_action_valid)
                level_path="/".join(name_before.split("_")[:-1])+"/"
                os.makedirs(data_output_path+level_path,mode=511,exist_ok=True)
                save_json(data_output_path+level_path+name_before+".json",data_json_before)
                break

            action_flag=1

            xml_after=xml_source[:]
            anytree_root = parse_xml_to_anytree(xml_source)
            html_code_after = any_tree_to_html(anytree_root, 0, None)

            ###################################################


            level_path_before="/".join(name_before.split("_")[:-1])+"/"
            os.makedirs(data_output_path+level_path_after,mode=511,exist_ok=True)

            screencap_command = f"adb -s {device_name} shell screencap -p >"+data_output_path+level_path_after+name_after+"-screen.png"
            subprocess.run(screencap_command,shell=True)

            save_txt(data_output_path+level_path_after+name_after+"-html.txt",html_code_after)
            save_txt(data_output_path+level_path_after+name_after+"-xml.txt",xml_after)

            if name_after not in all_page_id:
                page_id=len(all_page_id)
                all_page_id[name_after]=page_id
                save_dict(data_output_path+"all_page_id.json",all_page_id)

            all_triple["data"].append([name_before,action_index,name_after])
            all_triple["num"]=len(all_triple["data"])
            save_json(data_output_path+"all_triple.json",all_triple)
            #save_dict(data_output_path+"all_page_id.json",all_page_id)

            with open(data_output_path+level_path_after+name_after+"-html.txt", 'r', encoding='utf-8') as f:
                bm_query=f.readlines()
                f.close()
            history_list=data_json_before["history_actions"][:]
            history_list.append(action_res)
            temp_flag=0
            if appPackage not in html_code_after or len(history_list)==0:
                data_all2unique[name_after]=name_after #如果这个页面里面没有加载出可操作按钮，虽然他可能是一个新页面，但也只把它作为末尾，不放到unique_page里面了
            if name_after not in data_all2unique:

                diff_max=args.diff_max
                diff_png=args.diff_png
                #if len(html_code_after)>20:
                #    diff_max+=(len(html_code_after)-10)//10

                result_xml,result_images,result_nums,result_difs=compare_image_and_xml(
                    data_output_path+level_path_before+name_before+"-xml.txt", 
                    data_output_path+level_path_after+name_after+"-xml.txt", diff_max, 
                    data_output_path+level_path_before+name_before+"-screen.png", 
                    data_output_path+level_path_after+name_after+"-screen.png", diff_png)
                if result_xml==True and result_images==True:#compare to before page,same xml, same image, same page as before
                    if name_after not in data_unique2all[name_before]:
                        data_unique2all[name_before].append(name_after)
                    data_all2unique[name_after]=name_before
                    temp_flag=1
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(name_after)
                print(result_nums,result_difs)
                print(result_xml,result_images)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")




                if temp_flag==0: # new page,  compare to all old unique page, 
                    compare_index,compare_name=bm25.get_max(bm_query)
                    #for compare_name in data_unique2all:
                    level_compare_path="/".join(compare_name.split("_")[:-1])+"/"
                    print("##########################")
                    print(len(bm_query))
                    print(compare_index,compare_name)
                    print("##########################")
                    #print(len(html_code_after))
                    #input("Enter:")
                    result_xml,result_images,result_nums,result_difs=compare_image_and_xml(
                        data_output_path+level_path_after+name_after+"-xml.txt", 
                        data_output_path+level_compare_path+compare_name+"-xml.txt", diff_max, 
                        data_output_path+level_path_after+name_after+"-screen.png", 
                        data_output_path+level_compare_path+compare_name+"-screen.png", diff_png)
                    if result_xml==True and result_images==True:
                        if name_after not in data_unique2all[compare_name]:
                            data_unique2all[compare_name].append(name_after)
                        data_all2unique[name_after]=compare_name
                        temp_flag=1
                        #break
                if temp_flag==0: # new page, not same as any unique page
                    data_unique2all[name_after]=[name_after]
                    data_all2unique[name_after]=name_after
                    all_unique_page["data"].append({"round":round_number+1,"name":name_after,"name_id":all_page_id[name_after],
                        "history_actions":history_list,"num_actions":0,"failed":0})
                    all_unique_page["need"].append([len(all_unique_page["data"])-1,round_number])
                    all_unique_page["num"]=len(all_unique_page["data"])
                    save_json(data_output_path+"all_unique_page.json",all_unique_page)

                    bm25.appendItem(bm_query,name_after)


            unique_name_after=data_all2unique[name_after]
            if unique_name_after not in data_unique2action:
                data_unique2action[unique_name_after]=[]
            unique_name_before=data_all2unique[name_before]
            if action_res not in data_unique2action[unique_name_before]:
                data_unique2action[unique_name_before].append(action_res)
            save_dict(data_output_path+"data_unique2all.json",data_unique2all)
            save_dict(data_output_path+"data_all2unique.json",data_all2unique)
            save_dict(data_output_path+"data_unique2action.json",data_unique2action)

            data_json_after={"round":round_number+1, "name":name_after,"unique_name":data_all2unique[name_after],\
                "valid":True,"start_APP":data_json_before["start_APP"],"history_actions":history_list,\
                "action_valid":[], "action_invalid":[],"action_name_list":[],"parent":name_before}

            save_json(data_output_path+level_path_after+name_after+".json",data_json_after)

            temp_action_valid={"action_id":action_index,"action":action_res,"next_name":name_after,"next_unique":data_all2unique[name_after]}
            if temp_action_valid not in data_json_before["action_valid"]:
                data_json_before["action_valid"].append(temp_action_valid)
            if action_res not in data_json_before["action_name_list"]:
                data_json_before["action_name_list"].append(action_res)
            level_path_before="/".join(name_before.split("_")[:-1])+"/"
            os.makedirs(data_output_path+level_path_before,mode=511,exist_ok=True)
            save_json(data_output_path+level_path_before+name_before+".json",data_json_before)


            if appPackage not in html_code_after:
                close_webview_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "org.chromium.webview_shell"]
                subprocess.run(close_webview_command)
                close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
                subprocess.run(close_gallery_command)
                time.sleep(3)


            break



        if action_flag==0:
            all_unique_page["need"].pop(random_index)

    driver.quit()
    # task finished


