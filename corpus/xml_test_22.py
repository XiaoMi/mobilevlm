#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
# compare_image_and_xml(xml_path_1, xml_path_2, threshold_xml, screenshot_filepath_1, screenshot_filepath_2, threshold_image):


import argparse
import subprocess
import os, sys


sys.path.append(os.getcwd())
print(sys.path)
import time
from appium.webdriver.common.touch_action import TouchAction
# from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from appium import webdriver
from tqdm import tqdm
import PIL.Image

from agent_for_api.API_list import usr_api_list
from agent_for_api.agent_api_prompt import select_api_prompt, select_api_example
from agent_for_api.main_for_api import get_api_list
from agent_for_ui.agent_html_prompt import *
from selenium.common.exceptions import WebDriverException, InvalidElementStateException, NoSuchElementException
import json
from agent_for_ui.xml_to_html import any_tree_to_html
from chatgpt import chatgpt
#from gemini import gemini, gemini_img
import re
from app_list_MIUI import app_list
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

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



def compare_image_and_xml(xml_path_1, xml_path_2, threshold_xml, screenshot_filepath_1, screenshot_filepath_2, threshold_image):
    with open(xml_path_1, 'r', encoding='utf-8') as html_file:
        xml_1 = html_file.read()
    with open(xml_path_2, 'r', encoding='utf-8') as html_file:
        xml_2 = html_file.read()
    #result_xml = compare_xml(xml_1, xml_2, threshold_xml)
    result_xml = compare_actions(xml_1, xml_2, threshold_xml)
    result_images = compare_images(screenshot_filepath_1, screenshot_filepath_2, threshold_image)
    print(result_xml, result_images)

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
            time.sleep(5)  # Wait for 5 seconds before retrying
            # driver.quit()
            # driver = open_driver()
    return xml_source, driver



def open_driver(desired_caps):
    success = False
    attempt_count = 0
    while not success and attempt_count < max_attempts:
        try:
            driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
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
    with open(file_path, 'r', encoding='utf-8') as file:
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
    return dif_ratio < threshold

def getscreenshot(driver, screenshot_filename):
    # screenshot_filename = '../html/static/screenshot.jpg'
    driver.get_screenshot_as_file(screenshot_filename)
    print(f"截图已保存为：{screenshot_filename}")

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
    return normalized_difference < difference_limit

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
    return jaccard_similarity > difference_limit


def read_files_and_content(folder_path):
    xml_source = []

    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        if file.endswith(".html"):
            html_file_path = os.path.join(folder_path, file)

            # 读取HTML文件内容
            with open(html_file_path, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
                xml_source.append(html_content)



    return xml_source

def catch_files_and_content(directory_path):
    desired_caps = {
        "platformName": "Android",
        "deviceName": "emulator-5554",
        "platformVersion": "14.0",
        'automationName': 'uiautomator2',
        'noReset': True,
        # 'unicodeKeyboard': True,
        # 'resetKeyboard': False,
        'newCommandTimeout': 6000,
        'uiautomator2ServerLaunchTimeout': 60000
        # 'skipServerInstallation': 'false',
    }
    print("[start connected]")
    # driver to connect to the emulator
    xml_source = []
    driver = open_driver(desired_caps)
    label = 'yes'
    i = 0

    while label == 'yes':
        print(r"------------Round {round}------------".format(round=i))
        xml_source_now, driver = get_page_source(driver)
        xml_source.append(xml_source_now)
        anytree_root = parse_xml_to_anytree(xml_source_now)

        # print(xml_source)
        # print(xml_source_now)
        # translate xml to html
        filename = os.path.join(directory_path, f"xml_{i}.html")
        screenshot_filename = os.path.join(directory_path, f"xml_{i}.png")
        getscreenshot(driver, screenshot_filename)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(xml_source_now)
        html_code = any_tree_to_html(anytree_root, 0, None)
        print("[HTML UI]：", html_code) #[:400]
        label = input("[Please adjust the UI to the new interface and enter 'yes'. To end, enter 'no'.]: ")
        i += 1
    contrast_label = 'yes'
    driver.quit()
    return xml_source

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
        visible = has_text or has_content_desc or 'button' in element_type.lower()

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

def main():


    directory_path = 'xml_record_3'  # Adjust the path to your directory
    if not os.path.exists(directory_path):
        # 如果目录不存在，创建它
        os.makedirs(directory_path)
    #两种途径获取待比较的UI

    #从文件夹读取已保存xml和截图
    # xml_source = read_files_and_content(directory_path)
    #存储新的xml和截图, 每次手动调整到新UI后输入'yes'存储当前UI, 输入'no'结束存储UI部分
    xml_source = catch_files_and_content(directory_path)

    contrase_label = 'yes'
    i = 0
    while contrase_label == 'yes':
        num_1 = input("[Enter the 'first' page number to be compared (starting from 0]: ")
        num_2 = input("[Enter the 'second' page number to be compared (starting from 0]: ")
        try:
            num_1 = int(num_1)
            num_2 = int(num_2)
        except ValueError:
            # 如果转换失败，说明输入不是整数
            print("Incorrect input: Please enter a valid integer")
        else:
            # 现在 num_1 和 num_2 是整数，可以进行比较
            if num_1 >= len(xml_source) or num_1 < 0 or num_2 >= len(xml_source) or num_2 < 0:
                print("Incorrect input: Page number out of range")
            else:
                x = 10  #xml树结构差异大于x返回false
                result = compare_xml(xml_source[num_1], xml_source[num_2], x)


                screenshot_file_1 = os.path.join(directory_path, f"xml_{num_1}.png")
                screenshot_file_2 = os.path.join(directory_path, f"xml_{num_2}.png")

                image_result = compare_images(screenshot_file_1, screenshot_file_2, 0.8)
                print("[image]:", image_result)
        contrase_label = input("[continue enter 'yes'. To end, enter 'no']:")
    # task finished

if __name__ == '__main__':
    # main()
    #directory_path = 'xml_record_2'
    #directory_path ="corpus/random_walk/ctrip_unique"+"/"
    #xml_path_1 = os.path.join(directory_path, f"ctrip0-1-xml.txt")
    #xml_path_2 = os.path.join(directory_path, f"ctrip0-2-xml.txt")
    #screenshot_filepath_1 = os.path.join(directory_path, f"ctrip0-1-screen.png")
    #screenshot_filepath_2 = os.path.join(directory_path, f"ctrip0-2-screen.png")
    #xml_path_1 = os.path.join(directory_path, f"ctrip0/ctrip0_3c-1-xml.txt")
    #xml_path_2 = os.path.join(directory_path, f"ctrip0/ctrip0_3c-xml.txt")
    #screenshot_filepath_1 = os.path.join(directory_path, f"ctrip0/ctrip0_3c-1-xml.png")
    #screenshot_filepath_2 = os.path.join(directory_path, f"ctrip0/ctrip0_3c-xml.png")
    
    #directory_path ="corpus/random_walk/ctrip_graph"+"/"
    directory_path=sys.argv[1]
    path1=sys.argv[2]
    path2=sys.argv[3]
    print("#################")
    print(directory_path)
    print(path1)
    print(path2)
    #xml_path_1 = os.path.join(directory_path, f"ctrip0/ctrip0_38-xml.txt")
    #xml_path_1 = os.path.join(directory_path, f"ctrip0-xml.txt")
    #xml_path_2 = os.path.join(directory_path, f"ctrip0/ctrip0_39-xml.txt")
    #xml_path_2 = os.path.join(directory_path, f"ctrip0/ctrip0_40-xml.txt")
    xml_path_1 = os.path.join(directory_path, path1+"-xml.txt")
    xml_path_2 = os.path.join(directory_path, path2+"-xml.txt")
    screenshot_filepath_1 = os.path.join(directory_path, path1+"-screen.png")
    screenshot_filepath_2 = os.path.join(directory_path, path2+"-screen.png")
    #screenshot_filepath_2 = os.path.join(directory_path, f"ctrip0/ctrip0_40-screen.png")


    compare_image_and_xml(xml_path_1, xml_path_2, 10, screenshot_filepath_1, screenshot_filepath_2, 0.3)
