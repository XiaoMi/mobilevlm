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
from selenium.common.exceptions import WebDriverException, InvalidElementStateException, NoSuchElementException, InvalidArgumentException, StaleElementReferenceException

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
import shutil

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
import signal

def signal_handler(sig, frame):
    driver.quit()
    print("driver cleaned")
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


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
        l1 = find_element(text, driver)
        if l1 == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element click({text})"})
        elif len(l1) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element click({text})"})
        else:
            try:
                l1[0].click()
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
        l1 = find_element(text, driver)
        if l1 == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element press({text})"})
        elif len(l1) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element press({text})"})
        else:
            try:
                action.press(l1[0]).wait(1000).release().perform()
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
        l1 = find_element(text, driver)
        if l1 == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element Zoom({text})"})
        elif len(l1) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element Zoom({text})"})
        else:
            try:
                action1.press(l1[0]).move_to(x=0, y=-100)  # 向上移动
                action2.press(l1[0]).move_to(x=0, y=100)  # 向下移动
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
        l1 = find_element(text, driver)
        if l1 == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element pinch({text})"})
        elif len(l1) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element pinch({text})"})
        else:
            try:
                action1.press(x=l1[0].location['x'], y=l1[0].location['y'] - 100).move_to(l1[0])
                action2.press(x=l1[0].location['x'], y=l1[0].location['y'] + 100).move_to(l1[0])

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
        l1 = find_element(element, driver)
        if l1 == None:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element. input({element}, {input_context})"})
        elif len(l1) == 0:
            print("Warning: Invalid element")
            history_actions.append({"Action": f"[Fail]: Invalid element. input({element}, {input_context})"})
        else:
            try:
                # 点击元素
                l1[0].click()
                history_actions.append({"Action": f"click({element})"})
                try:
                    WebDriverWait(driver, 1).until(
                        EC.staleness_of(l1[0])
                    )
                    # 等待刷新

                except TimeoutException:
                    # 如果元素不存在或不可见，不执行input操作
                    l1[0].send_keys(input_context)
                    history_actions.append({"Action": f"input({element}, {input_context})"})

            except InvalidElementStateException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append(
                    {"Action": f"[Fail]: InvalidElementStateException input({element}, {input_context})"})
            except NoSuchElementException as e:
                print(f"Encountered an error: {e}. Retrying...")
                history_actions.append({"Action": f"[Fail]: NoSuchElementException input({element}, {input_context})"})
            except InvalidArgumentException as e:
                print(f"Encountered an error: {e}. Input value might be invalid for the element.")
                history_actions.append(
                    {"Action": f"[Fail]: InvalidArgumentException input({element}, {input_context})"})
            except StaleElementReferenceException as e:
                print(f"Encountered an error: {e}. The element might have been detached from the DOM.")
                history_actions.append(
                    {"Action": f"[Fail]: StaleElementReferenceException input({element}, {input_context})"})



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
                    #print(f"{index:{max_index_length}}: {description}")

                    action_space[index]=category_name
    return action_space

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

def restart_from_homepage(start_APP_command,history_list,driver,deviceName,waitadb,name_en):
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
    #while len(history_list)>1:
    #    flag=0
    for temp_command in history_list:

        if "adb shell" in temp_command:
            temp_command=set_adb(temp_command,deviceName)
        actions(temp_command, history_actions, driver)
        if "adb" in temp_command.lower():
            time.sleep(waitadb)
        else:
            time.sleep(3)
        if name_en !="supercaculator" and name_en != "keep":
            last_action_result=history_actions[-1]["Action"]
            if "[Fail]:" in last_action_result:
                flag=1
                break
    #    if flag==1:
    #        break
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
    parser.add_argument('--recheck',type=int, default=0)
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
    def printPara(self):
        print("len doc_names", len(self.doc_names))
        print("len docs", len(self.docs))
        #count=0
        #for word in self.df:
        #    print("BM25 word ", word)
        #    print("BM25 freq ", self.df[word])
        #    count+=1
        #    if count>10:
        #        break

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
        return False,False

    # Convert images to numpy arrays
    #print(img_path1)
    img1_array = np.array(img1)
    #print(img_path2)
    img2_array = np.array(img2)

    # Check if dimensions are the same
    if img1_array.shape != img2_array.shape:
        print("Images have different dimensions.")
        return False,False

    # Calculate the number of equal pixels
    equal_pixels = np.sum(img1_array == img2_array)

    # Total number of pixels
    total_pixels = img1_array.size

    # Calculate the ratio of equal pixels
    similarity_ratio = equal_pixels / total_pixels
    dif_ratio = 1 - similarity_ratio
    print("dif_ratio: ", dif_ratio)
    return dif_ratio < threshold, dif_ratio

def compare_actions(xml1,xml2, difference_limit):
    anytree_root_1 = parse_xml_to_anytree(xml1)
    html_1 = any_tree_to_html(anytree_root_1, 0, None)
    anytree_root_2 = parse_xml_to_anytree(xml2)
    html_2 = any_tree_to_html(anytree_root_2, 0, None)
    elements1 = set(html_1.strip().split("\n"))
    elements2 = set(html_2.strip().split("\n"))
    intersection = elements1.intersection(elements2)
    union = elements1.union(elements2)
    jaccard_similarity = len(intersection) / len(union) if len(union) > 0 else 0
    print(f"Jaccard Similarity: {jaccard_similarity}")
    return jaccard_similarity > difference_limit, jaccard_similarity



def compare_image_and_xml(xml_path_1, xml_path_2, threshold_xml, screenshot_filepath_1, screenshot_filepath_2, threshold_image):
    with open(xml_path_1, 'r', encoding='utf-8') as html_file:
        xml_1 = html_file.read()
    with open(xml_path_2, 'r', encoding='utf-8') as html_file:
        xml_2 = html_file.read()
    result_xml, result_nums = compare_actions(xml_1, xml_2, threshold_xml)
    result_images, result_difs = compare_images(screenshot_filepath_1, screenshot_filepath_2, threshold_image)
    return result_xml,result_images, result_nums, result_difs

def compare_unique(page1,page2,bm25,data_unique2all,data_all2unique,data_output_path,page2_dir,diff_max,diff_png):
    if len(page1)>1:
        result_xml,result_images,result_nums,result_difs=compare_image_and_xml(
            data_output_path+page2_dir+"/"+page2+"-xml.txt", 
            data_output_path+page2_dir+"/"+page1+"-xml.txt", diff_max, 
            data_output_path+page2_dir+"/"+page2+"-screen.png", 
            data_output_path+page2_dir+"/"+page1+"-screen.png", diff_png)
        temp_valid=True
        if result_xml==True and result_images==True:
            unique_name=data_all2unique[page1]
            if unique_name in data_unique2all:
                if page2 not in data_unique2all[unique_name]:
                    data_unique2all[unique_name].append(page2)
                data_all2unique[page2]=unique_name
                temp_valid=False
        if temp_valid==True:
            with open(data_output_path+page2_dir+"/"+page2+"-html.txt", 'r', encoding='utf-8') as f:
                bm_query=f.readlines()
                f.close()
            compare_index,compare_name=bm25.get_max(bm_query)
            result_xml,result_images,result_nums,result_difs=compare_image_and_xml(
                data_output_path+page2_dir+"/"+page2+"-xml.txt", 
                data_output_path+compare_name+"/"+compare_name+"-xml.txt", diff_max, 
                data_output_path+page2_dir+"/"+page2+"-screen.png", 
                data_output_path+compare_name+"/"+compare_name+"-screen.png", diff_png)
            if result_xml==True and result_images==True:
                if page2 not in data_unique2all[compare_name]:
                    data_unique2all[compare_name].append(page2)
                data_all2unique[page2]=compare_name
                temp_valid=False
            else:
                data_unique2all[page2]=[page2]
                data_all2unique[page2]=page2
                bm25.appendItem(bm_query,page2)
        bm25.printPara()
    return bm25,data_unique2all,data_all2unique
#bm25,data_unique2all,data_all2unique=compare_unique(page1,page2,bm25,data_unique2all,data_all2unique,data_output_path,diff_max,diff_png)

def check_index(index,all_unique_page,max_steps,data_all2unique):
    flag=True
    if all_unique_page["need"][index][1]>max_steps:
        return False
    name_before=all_unique_page["data"][index]["name"]
    if data_all2unique[name_before]!=name_before:
        return False
    #if recheck<=0:
    if all_unique_page["data"][index]["hold"]==True or all_unique_page["data"][index]["done"]==True:
        return False

    return True

def set_hold(name_prefix,start_index,all_unique_page,name_before_curr):
    max_len=len(all_unique_page["data"])
    for index in range(start_index,max_len):
        if all_unique_page["data"][index]["hold"]==False and all_unique_page["data"][index]["done"]==False:
            curr_name=all_unique_page["data"][index]["name"] 
            if curr_name.startswith(name_before_curr):
                all_unique_page["data"][index]["hold"]=True
    return all_unique_page

def get_action_by_id(all_action_id,id_):
    for action in all_action_id:
        if all_action_id[action]==id_:
            return action
    return None

def add_input(name,data_output_path):

    with open(data_output_path+name+"/"+name+"-html.txt", 'r', encoding='utf-8') as f:
        html_code_save=f.read()
    mapping = map_and_reverse_complete_interactive_elements(html_code_save)
    action_space=display_html_and_mapping(html_code_save, mapping)
    window_size = driver.get_window_size()
    action_list_save = gen_action_list(action_space,window_size,mapping)

    temp_data_json=load_json(data_output_path+name+"/"+name+".json")
    temp_data_json["action_space"]=action_list_save

    save_json(data_output_path+name+"/"+name+".json",temp_data_json)



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

    appPackage = args.appPackage
    device_name = args.device_name
    systemPort = args.systemPort
    command_executor=args.command_executor
    waitadb=args.waitadb
    recheck=args.recheck
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
    global driver
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
    start_APP_command=current_adb
    diff_max=args.diff_max
    diff_png=args.diff_png

    if name_en in app_package_data:
        name_ch=app_name_en_data[name_en]["name_ch"]
    else:
        name_ch=name_en
    data_output_path="corpus/arm_01/"+name_en+"_graph_"+str(systemPort)+"/"

    os.makedirs(data_output_path,mode=511,exist_ok=True)
    round_number=1

    task_continue=True
    max_steps=10
    
    close_webview_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "org.chromium.webview_shell"]
    subprocess.run(close_webview_command)
    close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
    subprocess.run(close_gallery_command)

    close_command = ["adb","-s", device_name , "shell", "am", "force-stop", appPackage]
    history_actions=[]
    subprocess.run(close_command)

    data_restart_path="corpus/random_walk/"+name_en+"_graph_"+str(systemPort)+"/"

    skip_keyword_list=["长辈模式","跟随系统","夜间","深色模式","上次网页","模式", "皮肤","skin manage","撤销授权","上车即连","青少年模式","全健康内容家长放心","儿童模式","专属卡通体验","专为长辈设计","退出账号","退出当前账号","退出登录","上次未关闭网页"]

    if name_en=="QQ":
        skip_keyword_list.append("退出")
        skip_keyword_list.append("夜间")
    elif name_en=="supercaculator":
        skip_keyword_list.append(" 皮肤 ")
        skip_keyword_list.append(" 深色模式 ")
        skip_keyword_list.append(" 已关闭 ")
        skip_keyword_list.append(" 默认启动 ")
    elif name_en=="qqlive":
        skip_keyword_list.append("外观设置")
    elif name_en=="QQmusic":
        skip_keyword_list.append("模式与自定义")
        skip_keyword_list.append("默认模式")
    elif name_en=="kuaishou":
        skip_keyword_list.append("package=\"com.smile.gifmaker\" class=\"android.widget.TextView\" clickable=\"true\"> 语言 </p>")
        skip_keyword_list.append("package=\"com.smile.gifmaker\" class=\"android.widget.TextView\" clickable=\"true\"> English </p>")
    elif name_en=="netmail":
        skip_keyword_list.append("Delete this account")
        skip_keyword_list.append("Sign out")

    
    restart_actions_dict={
    "keep":["click(<p id=\"com.gotokeep.keep:id/button_negative\" package=\"com.gotokeep.keep\" class=\"android.widget.TextView\" clickable=\"true\"> 先休息 </p>)",
            "click(<p id=\"com.gotokeep.keep:id/button_negative\" package=\"com.gotokeep.keep\" class=\"android.widget.TextView\" clickable=\"true\"> 不发了 </p>)",
            "click(<p id=\"com.gotokeep.keep:id/button_negative\" package=\"com.gotokeep.keep\" class=\"android.widget.TextView\" clickable=\"true\"> 退出 </p>)"],
    "seekbooks":["click(<p id =\"com.flyersoft.seekbooks:id/navigation_bar_item_small_label_view\" package = \"com.flyersoft.seekbooks\" class =\"android.widget.TextView\" clickable=\"true\" > 书架 </p>)"],
    "supercaculator":["click(<button id=\"android:id/button2\" package=\"com.jincheng.supercaculator\" class=\"android.widget.Button\" clickable=\"true\"> 以后再说 </button>)",
                    "click(<button id=\"android:id/button1\" package=\"com.jincheng.supercaculator\" class=\"android.widget.Button\" clickable=\"true\"> 确定 </button>)",
                    "click(<p id=\"com.jincheng.supercaculator:id/tv_basic\" package=\"com.jincheng.supercaculator\" class=\"android.widget.TextView\" clickable=\"true\"> 基础 </p>)"],
    "netmail":["click(<p package=\"com.netease.mobimail\" class=\"android.widget.TextView\" clickable=\"true\"> Delete draft </p>)"],
    "cloudweather":["click(<p package=\"com.nowcasting.activity\" class=\"android.widget.ImageView\" id=\"com.nowcasting.activity:id/iv_close\" clickable=\"true\"> </p>)"],
    "mtxx":["click(<p id=\"com.mt.mtxx.mtxx:id/K)\" package=\"com.mt.mtxx.mtxx\" class=\"android.widget.TextView\" clickable=\"true\"> Cancel </p>)"],
    "youdao":["click(<p package=\"com.youdao.dict\" class=\"android.widget.ImageView\" id=\"com.youdao.dict:id/iv_close\" clickable=\"true\">  </p>)"],
    "QQ":["click(<p package=\"com.tencent.mobileqq\" class=\"android.widget.CheckBox\" id=\"com.tencent.mobileqq:id/s1k\" clickable=\"true\"> </p>)",
        "click(<button id=\"com.tencent.mobileqq:id/n59\" package=\"com.tencent.mobileqq\" class=\"android.widget.Button\" clickable=\"true\"> 一键登录 </button>)"
    ],
    "xiaohongshu":["click(<button id=\"com.xingin.xhs:id/t8\" package=\"com.xingin.xhs\" class=\"android.widget.Button\" clickable=\"true\"> 稍后再说 </button>)"]
    }

    if not os.path.exists(data_output_path+name_en+"0/"):
        curr_path=name_en+"0"
        start_APP_command=current_adb
        history_actions=[]
        restart_from_homepage(start_APP_command,history_actions,driver,device_name,waitadb,name_en)
        history_actions=[]

        xml_source, driver = get_page_source(driver)
        if xml_source == None:
            xml_source, driver = get_page_source(driver)
        xml_code=xml_source[:]
        anytree_root = parse_xml_to_anytree(xml_source)
        # translate xml to html
        html_code = any_tree_to_html(anytree_root, 0, None)
        mapping = map_and_reverse_complete_interactive_elements(html_code)
        action_space = display_html_and_mapping(html_code, mapping)

        window_size = driver.get_window_size()
        action_list= gen_action_list(action_space,window_size,mapping)

        os.makedirs(data_output_path+curr_path+"/",mode=511,exist_ok=True)


        screencap_command = f"adb -s {device_name} shell screencap -p >"+data_output_path+curr_path+"/"+curr_path+"-screen.png"
        subprocess.run(screencap_command,shell=True)

        save_txt(data_output_path+curr_path+"/"+curr_path+"-html.txt",html_code)
        save_txt(data_output_path+curr_path+"/"+curr_path+"-xml.txt",xml_code)
        data_json_before={"round":round_number, "name":curr_path,"unique_name":curr_path,"valid":True,\
            "start_APP":start_APP_command,"history_actions":[],\
            "action_space":action_list,"path":[curr_path]}
        save_json(data_output_path+curr_path+"/"+curr_path+".json",data_json_before)

        all_unique_page={"num":0, "data":[],"need":[]}
        all_triple={"num":0,"data":[]}
        all_page_actions={"num":0, "data":[]}
        all_page_id={}
        all_action_id={}
    
        data_unique2all={}
        data_all2unique={}

        data_unique2all[curr_path]=[curr_path]
        data_all2unique[curr_path]=curr_path

        all_page_id[curr_path]=0


        all_unique_page["data"].append({"round":round_number,"name":curr_path,"name_id":all_page_id[curr_path],\
            "done":False, "hold":False})
        all_unique_page["need"].append([all_page_id[curr_path],round_number])
        all_unique_page["num"]=len(all_unique_page["data"])

        all_page_actions["data"].append({"name":curr_path,"action_valid":[],"action_invalid":[]})


        save_json(data_output_path+"all_unique_page.json",all_unique_page)
        save_json(data_output_path+"all_triple.json",all_triple)
        save_json(data_output_path+"all_page_actions.json",all_page_actions)

        save_dict(data_output_path+"all_page_id.json",all_page_id)
        save_dict(data_output_path+"all_action_id.json",all_action_id)

        save_dict(data_output_path+"data_unique2all.json",data_unique2all)
        save_dict(data_output_path+"data_all2unique.json",data_all2unique)


        close_webview_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "org.chromium.webview_shell"]
        subprocess.run(close_webview_command)
        close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
        subprocess.run(close_gallery_command)

        close_command = ["adb","-s", device_name , "shell", "am", "force-stop", appPackage]
        history_actions=[]
        subprocess.run(close_command)


    all_unique_page=load_json(data_output_path+"all_unique_page.json")#
    all_page_actions=load_json(data_output_path+"all_page_actions.json")#name, [action1,action2]

    data_unique2all=load_dict(data_output_path+"data_unique2all.json")#name, name
    data_all2unique=load_dict(data_output_path+"data_all2unique.json")#name [name,name_index]

    all_triple=load_json(data_output_path+"all_triple.json") #data:[page1,action,page2] page_id, action_id, page_id
    all_page_id=load_dict(data_output_path+"all_page_id.json") #page_name,page_id,
    all_action_id=load_dict(data_output_path+"all_action_id.json")#action_name, action_id

    docs=[]
    docs_names=[]
    index=0

    print("re-BM-Before:",len(data_unique2all))
    #time.sleep(5)
    #if False: 
    if True:
        for key in data_unique2all:
            if not os.path.exists(data_output_path+key+"/"+key+"-html.txt"):

                with open(data_output_path+key+"/"+key+"-xml.txt", 'r', encoding='utf-8') as f:
                    #xml_source=f.readlines()
                    xml_source = f.read()
                    anytree_root = parse_xml_to_anytree(str(xml_source))
                    html_code_before = any_tree_to_html(anytree_root, 0, None)
                    
                    save_txt(data_output_path+key+"/"+key+"-html.txt",html_code_before)

            with open(data_output_path+key+"/"+key+"-html.txt", 'r', encoding='utf-8') as f:
                html_code_save=f.readlines()
                #print(len(html_code_save))
                docs.append(html_code_save)
            docs_names.append(key)
            #index+=1

        # 初始化BM25模型并计算得分
        bm25 = BM25(docs,docs_names)
    else: #rebuild unique
        curr_path=name_en+"0"
        with open(data_output_path+curr_path+"/"+curr_path+"-html.txt", 'r', encoding='utf-8') as f:
            html_code_save=f.readlines()
            docs.append(html_code_save)
        docs_names.append(curr_path)
        bm25 = BM25(docs,docs_names)

        new_all2unique={}
        new_unique2all={}
        new_all2unique[curr_path]=curr_path
        new_unique2all[curr_path]=[curr_path]

        count_temp=0


        for page2 in data_all2unique:
            count_temp+=1
            page1="_".join(page2.split("_")[:-1])
            if len(page1)>1:
                result_xml,result_images,result_nums,result_difs=compare_image_and_xml(
                    data_output_path+page2+"/"+page2+"-xml.txt", 
                    data_output_path+page2+"/"+page1+"-xml.txt", diff_max, 
                    data_output_path+page2+"/"+page2+"-screen.png", 
                    data_output_path+page2+"/"+page1+"-screen.png", diff_png)
                temp_valid=True
                if result_xml==True and result_images==True:
                    unique_name=data_all2unique[page1]
                    if unique_name in new_unique2all:
                        if page2 not in new_unique2all[unique_name]:
                            new_unique2all[unique_name].append(page2)
                        new_all2unique[page2]=unique_name
                        temp_valid=False
                if temp_valid==True:
                    with open(data_output_path+page2+"/"+page2+"-html.txt", 'r', encoding='utf-8') as f:
                        bm_query=f.readlines()
                        f.close()
                    compare_index,compare_name=bm25.get_max(bm_query)
                    result_xml,result_images,result_nums,result_difs=compare_image_and_xml(
                        data_output_path+page2+"/"+page2+"-xml.txt", 
                        data_output_path+compare_name+"/"+compare_name+"-xml.txt", diff_max, 
                        data_output_path+page2+"/"+page2+"-screen.png", 
                        data_output_path+compare_name+"/"+compare_name+"-screen.png", diff_png)
                    if result_xml==True and result_images==True:
                        if page2 not in new_unique2all[compare_name]:
                            new_unique2all[compare_name].append(page2)
                        new_all2unique[page2]=compare_name
                        temp_valid=False
                    else:
                        new_unique2all[page2]=[page2]
                        new_all2unique[page2]=page2
                        bm25.appendItem(bm_query,page2)
                    #if count_temp>=100:
                    #    print(len(bm_query))
                    #    bm25.printPara()
                    #    print(len(new_unique2all))
                    #    print(len(new_all2unique))
                    #    time.sleep(3)

        bm25.printPara()
        save_dict(data_output_path+"data_unique2all.json",new_unique2all)
        save_dict(data_output_path+"data_all2unique.json",new_all2unique)
        data_unique2all=load_dict(data_output_path+"data_unique2all.json")#name, name
        data_all2unique=load_dict(data_output_path+"data_all2unique.json")#name [name,name_index]

    print("re-BM-After:",len(data_unique2all))

    for i in range(len(all_unique_page["data"])):
        assert all_unique_page["data"][i]["name_id"]== i
        assert all_page_actions["data"][i]["name"]== all_unique_page["data"][i]["name"]

    if recheck>0:
        for i in range(len(all_unique_page["data"])):
            all_unique_page["data"][i]["hold"]=False
            all_unique_page["data"][i]["done"]=False
            add_input(all_unique_page["data"][i]["name"],data_output_path)
    else:
        for i in range(len(all_unique_page["data"])):
            all_unique_page["data"][i]["hold"]=False

    html_code_after=[]
    count=0
    

    key_max_step=5

    all_data_index=0
    count_before_cycle=0

    #all_unique_page["data"].append({"round":round_number,"name":curr_path,"name_id":all_page_id[curr_path],\
    #    "done":False, "hold":False})
    #all_unique_page["need"].append([all_page_id[curr_path],round_number])
    #all_unique_page["num"]=len(all_unique_page["data"])

    random_index=0
    appium_unstable_flag=0
    while len(all_unique_page["need"])>0:
        index_flag=check_index(random_index,all_unique_page,max_steps,data_all2unique)
        if index_flag==False:
            if all_unique_page["need"][random_index][1]>3:
                random_index=random.randint(0,len(all_unique_page["need"])-1)
            else:
                random_index+=1
        index_flag=check_index(random_index,all_unique_page,max_steps,data_all2unique)
        if index_flag==False:
            max_len=len(all_unique_page["need"])
            temp_flag=0
            new_index=random_index

            for i in range(1,max_len):
                new_index=(i+random_index)%max_len
                index_flag=check_index(new_index,all_unique_page,max_steps,data_all2unique) 
                if index_flag==True:
                    temp_flag=1
                    break
            if temp_flag==0:
                break
            random_index=new_index

        all_data_index=all_unique_page["need"][random_index][0]
        name_before=all_unique_page["data"][all_data_index]["name"]

        
        temp_save_path="temp_save"
        os.makedirs(data_output_path+temp_save_path+"/",mode=511,exist_ok=True)

        history_actions=[]
        temp_actions=restart_from_homepage(start_APP_command,history_actions,driver,device_name,waitadb,name_en)
        print("all_data_index",all_data_index)
        print("name_before:",name_before)

        levellist=name_before.split("_")[:]
        path_list=[]
        his_list=[]
        last_action_result=[]
        skipFlag=False
        action_list_before=[]
        name_before_curr=""
        for i in range(len(levellist)):
            page1="_".join(levellist[:i])
            page2="_".join(levellist[:i+1])
            name_before_curr="_".join(levellist[:i+1])
            
            path_list.append(page2)

            if i !=0:
                action_index=int(levellist[i])
                action_res=get_action_by_id(all_action_id,action_index)
                print("need process",action_res)
                his_list.append(action_res)


                if action_res==None:
                    skipFlag=True
                for skipkeyword in skip_keyword_list:
                    if skipkeyword in action_res:
                        print("--------------------------")
                        print("skipkeyword in action_res")
                        print(action_res)
                        print(skipkeyword)
                        print("--------------------------")
                        skipFlag=True
                if action_res not in action_list_before and "scroll" not in action_res:
                    print("--------------------------")
                    print("action_res not in action_list_before")
                    print(action_res)
                    print(action_list_before)
                    print("--------------------------")
                    skipFlag=True
                    #print("not in action_list")
                    #print(action_res)
                    #print(action_list_before)
                if skipFlag ==False:
                    history_actions=["None"]
                    print("name_before_actions:",action_res)
                    actions(action_res,history_actions, driver)
                    time.sleep(3)
                    last_action_result=history_actions[-1]["Action"]

                if "[Fail]:" in last_action_result or skipFlag ==True:
                    all_unique_page["data"][all_data_index]["hold"]=True
                    shutil.rmtree(data_output_path+temp_save_path+"/")
                    skipFlag=True
                    break

            xml_source, driver = get_page_source(driver)

            #if xml_source == None:
            #    time.sleep(3)
            #    xml_source, driver = get_page_source(driver)
            if xml_source==None:
                print("--------------------------")
                print("xml_source==None")
                print(html_code_before)
                print(action_list_before)
                print("--------------------------")

                all_unique_page["data"][all_data_index]["hold"]=True
                shutil.rmtree(data_output_path+temp_save_path+"/")
                skipFlag=True
                if i==0:
                    appium_unstable_flag+=1
                if appium_unstable_flag>=3:
                    driver.quit()
                    print("driver cleaned")
                    sys.exit(0)
                break
            else:
                if i!=0:
                    appium_unstable_flag=0

            xml_code_before=xml_source[:]
            
            anytree_root = parse_xml_to_anytree(xml_source)
            html_code_before = any_tree_to_html(anytree_root, 0, None)
            mapping = map_and_reverse_complete_interactive_elements(html_code_before)
            action_space = display_html_and_mapping(html_code_before, mapping)
            window_size = driver.get_window_size()
            action_list_before= gen_action_list(action_space,window_size,mapping)

            if i==0: # main page has window
                if name_en in restart_actions_dict.keys():
                    history_actions=restart_actions_dict[name_en]
                    temp_history_actions=[]
                    for temp_command in history_actions: 
                        if temp_command in action_list_before:
                            actions(temp_command, temp_history_actions, driver)
                            print("page_start actions:",temp_command)
                            time.sleep(waitadb)

                            xml_source, driver = get_page_source(driver)
                            if xml_source==None:
                                all_unique_page["data"][all_data_index]["hold"]=True
                                shutil.rmtree(data_output_path+temp_save_path+"/")
                                skipFlag=True
                                appium_unstable_flag+=1
                                if appium_unstable_flag>=3:
                                    driver.quit()
                                    print("driver cleaned")
                                    sys.exit(0)
                                break
                            xml_code_before=xml_source[:]
                            anytree_root = parse_xml_to_anytree(xml_source)
                            html_code_before = any_tree_to_html(anytree_root, 0, None)
                            mapping = map_and_reverse_complete_interactive_elements(html_code_before)
                            action_space = display_html_and_mapping(html_code_before, mapping)
                            window_size = driver.get_window_size()
                            action_list_before= gen_action_list(action_space,window_size,mapping)



            screencap_command = f"adb -s {device_name} shell screencap -p >"+data_output_path+temp_save_path+"/"+page2+"-screen.png"
            subprocess.run(screencap_command,shell=True)

            save_txt(data_output_path+temp_save_path+"/"+page2+"-html.txt",html_code_before)
            save_txt(data_output_path+temp_save_path+"/"+page2+"-xml.txt",xml_code_before)
            temp_valid=False

            if data_all2unique[page2]==page2:
                temp_valid=True

            data_json_before={"round":i+1, "name":page2,"unique_name":data_all2unique[page2],"valid":temp_valid,\
                "start_APP":start_APP_command,"history_actions":his_list,\
                "action_space":action_list_before,"path":path_list}
            save_json(data_output_path+temp_save_path+"/"+page2+".json",data_json_before)

            if appPackage not in html_code_before: 
                print("--------------------------")
                print("appPackage not in html_code_before")
                print(html_code_before)
                print(action_list_before)
                print("--------------------------")

                all_unique_page["data"][all_data_index]["hold"]=True
                skipFlag=True
        print("skipFlag",skipFlag)
        #successfully process
        action_after_Flag=False
        action_fail_Flag=False
        html_code_after=[]

        if skipFlag==True:
            all_unique_page=set_hold(name_before,all_data_index,all_unique_page,name_before_curr)

        if skipFlag==False:
            all_unique_page["data"][all_data_index]["hold"]=False

            with open(data_output_path+name_before+"/"+name_before+"-html.txt", 'r', encoding='utf-8') as f:
                html_code_save=f.read()
            mapping = map_and_reverse_complete_interactive_elements(html_code_save)
            action_space=display_html_and_mapping(html_code_save, mapping)
            window_size = driver.get_window_size()
            action_list_save = gen_action_list(action_space,window_size,mapping)
            if len(action_list_save)<=5 and len(action_list_save)< len(action_list_before)-5:
                shutil.copy(data_output_path+temp_save_path+"/"+name_before+"-html.txt",
                    data_output_path+name_before+"/"+name_before+"-html.txt")
                shutil.copy(data_output_path+temp_save_path+"/"+name_before+"-xml.txt",
                    data_output_path+name_before+"/"+name_before+"-xml.txt")
                shutil.copy(data_output_path+temp_save_path+"/"+name_before+"-screen.png",
                    data_output_path+name_before+"/"+name_before+"-screen.png")
                shutil.copy(data_output_path+temp_save_path+"/"+name_before+".json",
                    data_output_path+name_before+"/"+name_before+".json")
                action_list_save=action_list_before[:]
            
            for action_res in action_list_before:
                if action_res not in action_list_save and "scroll" not in action_res: #保证每个指令都是第一次保存过，并且这次也出现了。像是广告指令就放弃吧
                    continue 

                for skipkeyword in skip_keyword_list:
                    if skipkeyword in action_res:
                        continue

                if action_res in all_action_id:
                    action_index=all_action_id[action_res]
                    name_after=name_before+"_"+str(action_index)
                    if name_after in data_all2unique:
                        continue
                else:
                    action_index=len(all_action_id)
                    all_action_id[action_res]=action_index
                    name_after=name_before+"_"+str(action_index)

                if action_index in all_page_actions["data"][all_data_index]["action_valid"] or action_index in all_page_actions["data"][all_data_index]["action_invalid"]:
                    continue


                if os.path.exists(data_output_path+name_after+"/"+name_after+".json"): #already have page
                    if name_after not in all_page_id:
                        page_id=len(all_page_id)
                        all_page_id[name_after]=page_id

                        all_unique_page["data"].append({"round":len(levellist),"name":name_after,"name_id":all_page_id[name_after],
                                "done":False, "hold":False})
                        all_unique_page["need"].append([all_page_id[name_after],len(levellist)])
                        all_unique_page["num"]=len(all_unique_page["data"])
                        
                        all_page_actions["data"].append({"name":name_after,"action_valid":[],"action_invalid":[]})
                        all_page_actions["num"]=len(all_page_actions["data"])


                        temp_l=[name_before,action_index,name_after]
                        if temp_l not in all_triple["data"]:
                            all_triple["data"].append(temp_l)
                            all_triple["num"]=len(all_triple["data"])

                        for i in range(len(all_page_actions["data"])):
                            temp_data=all_page_actions["data"][i]
                            if name_before==temp_data["name"]:
                                if action_res not in temp_data["action_valid"]:
                                    all_page_actions["data"][i]["action_valid"].append(action_index)

                        bm25,data_unique2all,data_all2unique=compare_unique(name_before,name_after,bm25,data_unique2all,data_all2unique,data_output_path,name_after,diff_max,diff_png)
                    continue


                #################process action_res

                his_list.append(action_res)
                path_list.append(name_after)
                history_actions=["None"]
                print("#########################")
                print(action_res)
                print("name_after",name_after)
                actions(action_res,history_actions, driver)
                action_after_Flag=True
                time.sleep(3)
                last_action_result=history_actions[-1]["Action"]


                xml_source, driver = get_page_source(driver)
                if xml_source == None:
                    time.sleep(3)
                    xml_source, driver = get_page_source(driver)

                if "[Fail]:" in last_action_result or xml_source==None or skipFlag ==True:
                    if action_index not in all_page_actions["data"][all_data_index]:
                        all_page_actions["data"][all_data_index]["action_invalid"].append(action_index)
                    #shutil.rmtree(data_output_path+page_name+"/")
                    action_fail_Flag=True
                    break

                xml_code_after=xml_source[:]
                
                anytree_root = parse_xml_to_anytree(xml_source)
                html_code_after = any_tree_to_html(anytree_root, 0, None)
                mapping = map_and_reverse_complete_interactive_elements(html_code_after)
                action_space = display_html_and_mapping(html_code_after, mapping)
                window_size = driver.get_window_size()
                action_list_after= gen_action_list(action_space,window_size,mapping)


                screencap_command = f"adb -s {device_name} shell screencap -p >"+data_output_path+temp_save_path+"/"+name_after+"-screen.png"
                subprocess.run(screencap_command,shell=True)

                save_txt(data_output_path+temp_save_path+"/"+name_after+"-html.txt",html_code_after)
                save_txt(data_output_path+temp_save_path+"/"+name_after+"-xml.txt",xml_code_after)

                bm25,data_unique2all,data_all2unique=compare_unique(name_before,name_after,bm25,data_unique2all,\
                    data_all2unique,data_output_path,temp_save_path,diff_max,diff_png)


                levellist=name_after.split("_")[:]
                temp_valid=False
                if data_all2unique[name_after]==name_after:
                    temp_valid=True

                data_json_after={"round":len(levellist), "name":name_after,"unique_name":data_all2unique[name_after],"valid":temp_valid,\
                    "start_APP":start_APP_command,"history_actions":his_list,\
                    "action_space":action_list_after,"path":path_list}
                save_json(data_output_path+temp_save_path+"/"+name_after+".json",data_json_after)

                if name_after not in all_page_id:
                    page_id=len(all_page_id)
                    all_page_id[name_after]=page_id

                    dataDone=False
                    if appPackage not in html_code_after:
                        dataDone=True

                    all_unique_page["data"].append({"round":len(levellist),"name":name_after,"name_id":all_page_id[name_after],
                            "done":dataDone, "hold":False})
                    all_unique_page["need"].append([all_page_id[name_after],len(levellist)])
                    all_unique_page["num"]=len(all_unique_page["data"])
                    
                    all_page_actions["data"].append({"name":name_after,"action_valid":[],"action_invalid":[]})
                    all_page_actions["num"]=len(all_page_actions["data"])


                    temp_l=[name_before,action_index,name_after]
                    if temp_l not in all_triple["data"]:
                        all_triple["data"].append(temp_l)
                        all_triple["num"]=len(all_triple["data"])

                    if action_index not in all_page_actions["data"][all_data_index]:
                        all_page_actions["data"][all_data_index]["action_valid"].append(action_index)

                if  not os.path.exists(data_output_path+name_after+"/"):
                    os.rename(data_output_path+temp_save_path+"/",data_output_path+name_after+"/")
                else:
                    shutil.rmtree(data_output_path+name_after+"/")
                    os.rename(data_output_path+temp_save_path+"/",data_output_path+name_after+"/")
                break

            #no process able actions
            if action_after_Flag==False: 
                all_unique_page["data"][all_data_index]["done"]=True
            else:
                all_unique_page["data"][all_data_index]["done"]=False
            #if action_fail_Flag==True:
            #    #process_error



            if action_after_Flag==True:

                print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("page num", len(all_unique_page["data"]))

            print("action_after_Flag: ([false,false] not processable actions for this page_before)", action_after_Flag)
            print("action_fail_Flag: ([True,true],process but failed| [True,False]:processed and succeed)", action_fail_Flag)

        save_json(data_output_path+"all_unique_page.json",all_unique_page)
        save_json(data_output_path+"all_triple.json",all_triple)
        save_json(data_output_path+"all_page_actions.json",all_page_actions)

        save_dict(data_output_path+"all_page_id.json",all_page_id)
        save_dict(data_output_path+"all_action_id.json",all_action_id)

        save_dict(data_output_path+"data_unique2all.json",data_unique2all)
        save_dict(data_output_path+"data_all2unique.json",data_all2unique)



        #print(appPackage)
        #input("here1")

        #if isinstance(html_code_after,list):
        #    html_code_line="".join(html_code_after)
        #else:
        #    html_code_line=html_code_after[:]
        outsideFlag=False
        if skipFlag==False and appPackage not in html_code_after:
            outsideFlag=True
        if skipFlag==True and appPackage not in html_code_before:
            outsideFlag=True

        if outsideFlag==True:

            xml_source, driver = get_page_source(driver)
            anytree_root = parse_xml_to_anytree(xml_source)
            html_code_line = any_tree_to_html(anytree_root, 0, None)
            match = re.search(r'package="([^"]+)"', html_code_line)

            if match:
                package_other = match.group(1)
                if package_other != 'com.android.systemui' and package_other != 'com.android.settings':
                    close_webview_command = ["adb", "-s", device_name, "shell", "am", "force-stop", package_other]
                    subprocess.run(close_webview_command)
                else:
                    go_back_command = ["adb", "-s", device_name, "shell", "input", "keyevent", "KEYCODE_BACK"]
                    subprocess.run(go_back_command)
                print(package_other)
                print(close_webview_command)
            else:
                package_other = None
                go_back_command = ["adb", "-s" ,device_name,"shell","input", "keyevent", "KEYCODE_BACK"]
                subprocess.run(go_back_command)

                close_webview_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "org.chromium.webview_shell"]
                subprocess.run(close_webview_command)
                close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
                subprocess.run(close_gallery_command)
            time.sleep(3)
        #input("here2")

        close_webview_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "org.chromium.webview_shell"]
        subprocess.run(close_webview_command)
        close_gallery_command = ["adb", "-s" ,device_name,"shell", "am", "force-stop", "com.android.gallery3d"]
        subprocess.run(close_gallery_command)

        close_command = ["adb","-s", device_name , "shell", "am", "force-stop", appPackage]
        history_actions=[]
        subprocess.run(close_command)
        print(" ".join(close_command))
        #input("here3")




    driver.quit()
    # task finished


