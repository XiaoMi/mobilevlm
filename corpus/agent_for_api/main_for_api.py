#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
import requests
import subprocess
from agent_for_api.agent_api_prompt import *
# from chatgpt import *
from agent_for_api.API_list import *
import socket
import argparse
import subprocess
import sys
import time
from appium import webdriver
from tqdm import tqdm
from agent_for_api.API_list import usr_api_list
from selenium.common.exceptions import WebDriverException, InvalidElementStateException, NoSuchElementException
# 选择api接口， 合成一个adb的指令，
def calculate(expression): # use a http api
    try:
        # 向计算器 API 发送 POST 请求
        api_url = "https://api.calculator.com/calculate" # 这个接口是外在接口，而不是手机内部的。
        data = {"expression": expression}
        response = requests.post(api_url, json=data)

        # 解析 API 响应
        if response.status_code == 200:
            result = response.json()
            return result["result"]
        else:
            return "Error: Unable to calculate."

    except Exception as e:
        return "Error: " + str(e)

def contact_command(contact_number, message_body):
    adb_command = [
        'adb', 'shell', 'am', 'start',
        '-a', 'android.intent.action.SENDTO',
        '-d', 'sms:', f'{contact_number}',
        '--es', 'sms_body', f'{message_body}'
    ]
    return adb_command

def build_command(title, task_description, starttime, endtime):
    adb_command = [
        'adb', 'shell', 'am', 'start',
        '-a', 'android.intent.action.INSERT',
        '-t', 'vnd.android.cursor.item/event',
        '-e', 'title', f'{title}',
        '-e', 'begin', f'{starttime}',
        '-e', 'end', f'{endtime}',
        '--ei', 'allDay', '0',
        '--es', 'description', f'{task_description}',
        '--ez', 'hasAlarm', '1'
        # '--ez',
        # 'android.intent.extra.REFRESH',
        # 'false'
    ]
    print(adb_command)
    return adb_command

def get_api_list(mode):
    api_list = []
    if mode == 'usr':
        api_list = usr_api_list
    elif mode == 'system':
        api_list = system_api_list
    return api_list

# 定义信息结构体列表
history_actions = []

def get_memory(history_actions):
    memory_list = []
    for round_number, action_info in enumerate(history_actions, 1):
        action = action_info['action']
        memory_list.append(f"Round {round_number}: Action: {action}")
    memory = "\n".join(memory_list)
    return memory
def is_port_open(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(('127.0.0.1', port))
        return False  # 端口已被占用
    except (ConnectionRefusedError, socket.timeout):
        return True  # 端口可用

max_attempts = 5  # Set the maximum number of retry attempts
def open_driver():
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


# add contact person
if __name__ == '__main__':
    desired_caps = {
        "platformName": "Android",  # 操作系统
        "deviceName": "emulator-5554",
        "platformVersion": "14.0",
        'automationName': 'uiautomator2',
        'noReset': True,
        'unicodeKeyboard': True,
        'resetKeyboard': False,
        # "skipServerInstallation": "false",
    }
    print("[start connected]")
    # driver to connect to the emulator
    driver = open_driver()
    adb = 'adb shell am start -a android.intent.action.VIEW -n com.xiaomi.market/.business_ui.useragreement.basicmode.BasicModeAgreementActivity -d "mimarket://agreement/basicmode"'
    subprocess.run(adb)
    driver.quit()
    # task = '提醒我下午五点去接孩子，在红星幼儿园。'
    # # 在ui和api之间抉择时，选定调用api作为下一个步骤。
    # # 获取当前页面的任务状态，他可能已经进行到中间步骤了。
    #
    # # prompt = select_api_prompt.format(select_api_example=select_api_example, api_list=get_api_list('usr'), task=task)
    # # # print(prompt)
    # # res = chatgpt(prompt)
    # # print("adb command: ", res)
    # # 解析api&参数
    # '''
    # 这部分是将api包装成adb指令，然后运行，adb的缺陷是动作完成后普遍需要用户确认。
    # '''
    # # adb_command = res
    # #
    # command = "adb shell am start -n com.traveloka.android/.appentry.splash.SplashActivity"
    # # 使用subprocess执行ADB命令
    # result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #
    # # 获取标准输出
    # stdout = result.stdout
    # print("stdout: ", stdout)
    # # 获取标准错误
    # stderr = result.stderr
    # print("stderr: ", stderr)
    # if not stderr:
    #     print("api correct")
    # # 获取返回代码
    # return_code = result.returncode
    # print("return_code: ", return_code)
    #

    # url = 'http://127.0.0.1:12345'
    # data = {
    #     "apiName": "---",
    #     "params": {
    #         "noteKey": "----",
    #         "noteContent": "----"
    #     }
    # }
    #
    # '''
    # 这部分是将api和参数包装成url包，发给我们自定义的apk
    # '''
    # try:
    #     response = requests.post(url, json=data)
    #     print("Response Status:", response.status_code)
    #     print("Response Body:", response.text)
    # except requests.exceptions.RequestException as e:
    #     print("Error:", e)
    #
    # # port_to_check = 12345  # 你要检查的端口
    # # if is_port_open(port_to_check):
    # #     print(f"Port {port_to_check} is available.")
    # # else:
    # #     print(f"Port {port_to_check} is already in use.")
