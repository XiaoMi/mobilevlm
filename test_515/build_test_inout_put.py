#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.      
import os
import shutil
import random
from tqdm import tqdm
import re
import random
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import xml.etree.ElementTree as ET
from anytree import Node
import json
import shutil
root_dir = '/data/xwk/log/ctrip_action2test'
# Example usage
intros = [
        "这是一个非常有帮助的应用程序",
        "这是一个对你日常任务至关重要的应用",
        "这个应用的功能十分强大",
        "用这个了不起的应用可以释放你的生产力",
        "可以说，这是一个高效的应用",
        "这是这个多功能应用的页面之一",
        "用这个应用可以革新你的日常生活流程",
        "用这个高效能应用可以完成更多工作",
        "用这个用户友好的应用可以简化你的生活",
        "通过这个优秀的应用可最大化效率",
        "通过这个尖端应用可以增强你的体验",
        "这展示了这个应用无与伦比的实用性",
        "这展示了这个强大应用的功能性潜力",
        "与这个先进的应用一起步入未来",
        "通过这个全面的应用可提升你的日常生活",
        "这展示了一个备受赞誉的应用",
        "这是一个不可或缺的应用",
        "用这个实用的应用使你的任务变得更容易",
        "深入探索这个杰出应用的丰富功能，它可以提升你的效率",
        "这个应用在其领域是一个游戏改变者",
        "用这个强大的应用优化你的日常流程"
]

icons_intro = [
    "它具有以下可操作的控制",
    "它具备以下互动控制功能",
    "它包含这些用户可操作的控制",
    "它配备以下可自定义的控制",
    "它提供这些可调控制以增强可用性",
    "它提供以下用于用户互动的控制",
    "它配有以下功能性控制",
    "它具有这些易于访问的控制",
    "它拥有多种可操作的控制",
    "它允许操作以下控制",
    "它包括这些用于用户参与的控制",
    "它整合了这些控制，以提供更好的用户体验",
    "它包含以下用于用户操作的控制",
    "它支持这些可操作的控制以更好的互动",
    "它具有这些控制，允许进行各种用户互动",
    "它包含这些用户可以轻松操作的控制",
    "它设计有以下用于用户操作的控制",
    "它呈现这些控制，以直观的用户操作",
    "它已集成以下用户友好的控制",
    "它旨在包括这些可调控制",
    "它提供以下一套控制，供用户自定义"
]

page_description_instruction = [
    "根据图片及其文本描述这幅图片。",
    "给我一个关于这幅图像的总结。",
    "你在图片中看到了什么？",
    "告诉我关于这张图片的信息。",
    "向我解释这幅图像。",
    "分解照片中的内容。",
    "图片中描绘了什么？",
    "描述图像的内容。",
    "传达图像的本质。",
    "详细说明这张图片。",
    "你能详细描述这幅图像吗？",
    "提供这张图片的概述。",
    "带我了解这幅图像。",
    "这幅图像展示了什么？",
    "为我描述这张图片。",
    "描述图像。",
    "你能说明图像中的内容吗？",
    "讨论图片的元素。",
    "提供对这幅图像的见解。",
    "这张照片中发生了什么？",
    "这张图片中发生了什么？请简短回答。",
    "简要地说出这个场景的内容",
    "用简短的文字展示照片中的内容。",
    "请用几句话描述图像的内容。",
    "图像的内容是什么？请用简短的句子回答。",
    "你能给我简要描述这幅图像吗？",
    "你在这张图片中看到了什么？",
    "用几句话描述图像的内容。",
    "提供这张照片的简洁解释。",
    "这个场景中发生了什么？",
    "总结照片的内容。",
    "图像中有哪些主要元素？",
    "快速解释这个视觉内容。",
    "简而言之，你能说这张图片表达了什么？",
    "图像的主要主题是什么？",
    "描述图像的主要特征。",
    "这张照片中描绘了什么？",
    "给我一个图片的简短描述。",
    "简要描述图像中的对象和动作。",
    "这幅图像的背景是什么？",
    "图像中显示了哪些关键元素？",
    "照片的主要主题是什么？",
    "用几句话告诉我你在这幅图像中看到了什么。",
    "图像的本质是什么？",
    "给我简要地分析图像中发生的事情。",
    "这幅图片代表了什么？",
    "用简单的话告诉我图像显示了什么。",
    "快速提及图像的内容。",
    "描述图像中发生的一般情景。",
    "你能总结这幅图像的主要方面吗？",
    "简要指出图像的重要方面。",
    "图中描绘的核心主题是什么？",
    "简要告诉我图像的中心主题。",
    "我应该在这幅图像中寻找什么重要特征？",
    "描述照片的主要元素。",
    "用一两句话描述这幅图像。",
    "概述这幅图像的主要内容。",
    "图片捕捉到了什么事件？",
    "简单地说，图像中显示了什么？",
    "你立刻在图像中注意到了什么？",
    "提供对图像的简要解释。",
    "告诉我这幅图像中发生的关键事情。",
    "表达这张照片的一般主题。",
    "这幅图像的核心内容是什么？"
]
page_action_space_instruction = [
    "这个页面包含了哪些可以互动的控件？",
    "描述这个页面上所有可以操作的控件。",
    "列出这个页面上可以与之互动的所有组件。",
    "这个页面提供了哪些互动元素？",
    "探索这个页面，找出所有可以操作的控件。",
    "可以与这个页面的哪些元素进行互动？",
    "这个页面中，哪些控件是可互动的？",
    "识别并描述这个页面上所有的互动组件。",
    "这个页面有哪些控件可以被操控？",
    "列举这个页面上可以互动的所有控件。",
    "这个页面中提供了哪些互动选项？",
    "这个页面包括了哪些可操作的用户界面元素？",
    "概述这个页面上所有可用于互动的控件。",
    "哪些控件在这个页面上可用，并且可以与之互动？",
    "这个页面中的互动组件有哪些？",
    "这个页面允许与哪些元素进行互动？",
    "详细描述这个页面上所有可以互动的控件。",
    "这个页面中有哪些元素可以进行操作和互动？",
    "告诉我这个页面上有哪些可互动的控件。",
    "你可以与这个页面的哪些部分进行互动？",
    "审视这个页面，指出所有的互动可能性。",
    "探讨这个页面的互动功能，列出可操作的控件。",
    "这个页面的交互设计包括哪些元素？",
    "查找并列出这个页面上的所有可互动控件。",
    "这个页面中哪些功能可以与用户直接互动？",
    "评估这个页面，描述可以互动的所有UI组件。",
    "探讨这个页面提供的用户交互选项。",
    "这个页面的哪些部分是可点击的？",
    "列出并描述这个页面上你可以互动的控件和按钮。",
    "这个页面的互动控件有哪些，它们如何影响用户体验？",
    "识别这个页面上所有可以触摸或点击的元素。",
    "这个页面上有哪些元素支持拖拽操作？",
    "在这个页面上，哪些部分可以响应用户的输入？",
    "概述这个页面中的所有可点击或可滑动的控件。",
    "描述这个页面上那些能够响应用户互动的控件。"
]


next_page_action_instruction = [
    "执行哪个操作可以从第一张图片导航到第二张图片？",
    "要从第一张图片到达第二张图片，需要激活哪个按钮？",
    "从第一张图片转到第二张图片需要与第一张图片的哪个界面元素进行交互？",
    "与第一张图片的哪个部分互动才能到达第二张图片？",
    "要从第一张图片到达第二张图片，必须使用第一张图片的哪个控件？",
    "确定在第一张图片上需要采取的操作以显示第二张图片。",
    "在第一张图片上需要点击或滑动或输入什么才能访问第二张图片？",
    "要前进到显示第二张图片的页面，你应该按下或滑动或输入什么？",
    "确定从第一张图片导航至第二张图片的控件。",
    "选择必须激活的第一张图片界面组件以找到第二张图片。",
    "在第一张图片上执行哪个操作将带你到第二张图片？",
    "描述在第一张图片上需要采取的步骤以找到第二张图片。",
    "第一张图片上的哪个控件操作会引导你到展示第二张图片的页面？",
    "在第一张图片上什么手势会导致探索第二张图片？",
    "选择在第一张图片上需要的互动以访问第二张图片。",
    "在第一张图片上必须操作什么才能到达第二张图片？",
    "哪个控件必须被操作以访问第二张图片？",
    "我需要操作什么来找到第二张图片？",
    "通过与第一张图片互动，我如何到达第二张图片？",
    "哪个按钮通向关于第二张图片的内容？",
    "我应该点击哪里以导航到第二张图片？",
    "哪个动作会带我到第二张图片？",
    "我应该选择什么来到达第二张图片？",
    "哪个控件可以直接到第二张图片？",
    "如何操作可以访问到第二张图片的页面？",
    "我应该与哪个界面元素互动来找到第二张图片？",
    "如何到达第二张图片的页面？",
    "这个界面的哪个部分通向第二张图片？",
    "必须操控什么才能看到第二张图片？",
    "我在哪里操作以到达第二张图片？",
    "我应该执行什么操作以访问第二张图片？",
    "哪个动作来到达展示第二张图片的页面？",
    "我应该使用什么控制来导航到第二张图片？",
    "如何到达第二张图片的页面？",
    "哪个控件操作导向了第二张图片？"
]
icon_location_instruction = [
    "“{text}”在界面中的什么位置？",
    "帮我定位“{text}”的位置。",
    "“{text}”的位置坐标是什么？",
    "“{text}”位于界面的哪个位置？",
    "请描述“{text}”在屏幕上的具体位置。",
    "我如何找到界面中的“{text}”？",
    "指出“{text}”在页面上的位置。",
    "在界面上，“{text}”位于什么地方？",
    "定位“{text}”在屏幕上的位置。",
    "请指明“{text}”在这个界面的具体位置。",
    "“{text}”在此界面中处于哪个地方？",
    "哪里可以找到“{text}”？请指出其位置。",
    "在页面布局中，“{text}”的精确位置是什么？",
    "告诉我“{text}”在界面上的位置坐标。",
    "“{text}”位于我们的应用界面的哪个地方？",
    "描述“{text}”在界面中的定位。",
    "寻找“{text}”，并指出它在页面上的位置。",
    "找出“{text}”在屏幕上的位置。",
    "请提供“{text}”在界面中位置的详细描述。",
    "你能指出“{text}”在这个界面上的位置吗？",
    "探索界面以找到“{text}”的确切位置。",
    "以坐标的方式描述“{text}”在界面中的定位。",
    "界面中“{text}”的定位点是哪里？",
    "搜寻并定位界面上的“{text}”。",
    "如何快速找到页面上的“{text}”？",
    "如何定位到界面中的“{text}”。",
    "分析并指示“{text}”在页面上的位置。",
    "界面布局中“{text}”处于何方？",
    "识别“{text}”在当前屏幕的位置。",
    "界面中的“{text}”位于哪个地方？",
    "解释“{text}”在此界面上的具体位置。",
    "能否详细说明“{text}”在界面上的位置？",
    "有关“{text}”的位置，请提供文本坐标描述。",
    "查找“{text}”在该页面的坐标。",
    "请标出“{text}”在界面上的位置。",
    "详细描述“{text}”在页面上的位置。",
    "在此应用界面中，“{text}”的位置如何？",
    "在屏幕布局中寻找“{text}”的位置。",
    "为我指明“{text}”在屏幕上的具体位置。",
    "有谁能告诉我“{text}”在界面中的定位？",
    "我怎样才能看到“{text}”在页面上的位置？",
    "请帮助我识别“{text}”在这个屏幕上的位置。",
    "在界面上定位“{text}”的结果是什么？",
    "请描绘“{text}”在屏幕中的位置。",
    "从界面的哪个部分可以找到“{text}”？",
    "提供一个关于“{text}”位置的简单说明。",
    "如何确定“{text}”在页面上的具体位置？",
    "请描述“{text}”在整个界面中的坐标位置。",
    "指导我找到“{text}”在这个应用页面中的位置。",
    "请问“{text}”在界面的哪个部位？",
    "我如何确认“{text}”在界面上的准确位置？",
    "描述在界面中寻找“{text}”的结果。"
]
page_structure_instruction = [
    "请描述当前页面的结构。",
    "告诉我当前页面元素之间的位置关系。",
    "总结当前页面的各个元素的位置。",
    "解释这个页面的布局和元素之间的相互关系。",
    "如何描述当前页面中各个组件的布局？",
    "请概述页面的整体结构及其功能区域。",
    "细述当前页面的设计和元素排列。",
    "描述这个界面的组成，包括所有可见的控件。",
    "界面中的元素是如何组织的？请提供详细描述。",
    "这个页面的布局是怎样的？说明元素的相对位置。",
    "请指出页面中各元素的相对位置和功能。",
    "当前页面有哪些主要的布局区块？描述它们的位置和功能。",
    "讨论当前页面的布局策略及其适用性。",
    "概述页面中各个部分的布局和互动方式。",
    "描述这个页面中的导航结构和内容元素。",
    "如何分析这个页面的元素布局？",
    "详细描述当前页面中各个元素的功能和位置。",
    "请说明这个页面上每个区域的用途和布局。",
    "描述当前屏幕的用户界面布局和元素交互。",
    "概述当前页面的视觉结构和元素对齐方式。",
    "评价当前页面的设计结构，包括元素如何协同工作。",
    "详述页面中各个元素的布局及其相互关系。",
    "描绘当前页面的整体布局，包括关键元素和功能。",
    "解释页面布局中各个元素的位置关系和交互逻辑。",
    "讨论当前页面中元素的视觉和功能层次结构。",
    "请描写这个界面的布局和元素的视觉流动性。",
    "从用户体验角度，描述当前页面的布局。",
    "详解当前页面的布局及其对用户交互的影响。",
    "概述当前页面的组件和它们的布局顺序。",
    "请描述页面元素之间的层次关系和空间分布。",
    "界面设计中，各元素是如何配合工作的？请描述其结构。",
    "解释当前页面的空间组织和元素间的动态关系。",
    "如何从结构层面解读当前的页面布局？",
    "概述页面中主要元素的空间布局和功能。",
    "详细解释页面中的交互元素和它们的布局逻辑。",
    "提供当前页面元素间相互关系的视觉图解。",
    "描述当前页面的信息架构和用户界面组件。",
    "总结当前页面中主要的视觉元素及其结构性。",
    "探讨这个页面的组件是如何布局以促进用户流动性的。",
    "页面的元素是如何排列的？",
    "说明当前页面的布局是如何满足功能需求的。",
    "描述在当前页面中，重要元素的布局策略。",
    "概述当前页面的互动元素及其功能定位。",
    "评述当前页面布局的有效性和用户互动方式。",
    "从设计角度讲，当前页面的元素是如何组织的？",
    "界面中各个元素的布局有何意义？请解析。",
    "阐释当前页面的元素如何支持其内容和功能。",
    "请描述当前页面中各个互动组件的位置关系。"
]

app_name = "携程"



def process_html(html):
    # 初始化列表
    inputs = []
    icons = []
    bounds = []

    # 分割HTML内容为逐行处理
    lines = html.strip().split('\n')

    # 遍历每一行HTML
    for line in lines:
        count = 1
        # 处理输入框
        if '<input' in line:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line)
            if text_match:  # 确保找到匹配项
                text = text_match.group(1).strip()
            else:
                text = None

            if text:
                inputs.append(text)
            else:
                inputs.append(f"第{count}个空白输入框")

        # 处理可点击元素
        if 'clickable="true"' in line:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line)
            if text_match:
                text = text_match.group(1).strip()
                if re.search("[\u4e00-\u9fa5]+", text):  # 检查是否包含汉字
                    icons.append(text)
                    continue

            alt_match = re.search(r'description="([^"]+)"', line)
            if alt_match:
                alt = alt_match.group(1).strip()
                if re.search("[\u4e00-\u9fa5]+", alt):
                    icons.append(alt)
                    continue

        # 处理可滚动元素
        if 'scrollable="true"' in line:
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
                bounds.append(bounds_text)

    # 函数结束后返回结果
    return inputs, icons, bounds


def actions_generate(html, xml):
    # 初始化列表
    inputs = []
    icons = []
    bounds = []
    anytree_root = parse_xml_to_anytree(xml)
    new_html = any_tree_to_html(anytree_root, 0, None)
    # 分割HTML内容为逐行处理
    lines1 = html.strip().split('\n')
    lines2 = new_html.strip().split('\n')
    html2action = {}

    # 遍历每一行HTML
    for line, line2 in zip(lines1, lines2):
        # 处理输入框
        count = 1
        if '<input' in line:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line)
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line2)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
            if text_match:  # 确保找到匹配项
                text = text_match.group(1)
            else:
                text = None
            if text:
                if text != ' ':
                    inputs.append(f"input(带有文本{text}的输入框, {bounds_text})")
                    html2action[f"带有文本{text}的输入框, {bounds_text}"] = line
                    continue
                else:
                    inputs.append(f"input(第{count}个空白输入框, {bounds_text})")
                    html2action[f"第{count}个空白输入框, {bounds_text}"] = line
                    count += 1
                    continue

        # 处理可点击元素
        if 'clickable="true"' in line:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line)
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line2)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
            if text_match:
                text = text_match.group(1).strip()
                if text and text != ' ':
                    icons.append(f"click({text}, {bounds_text})")
                    html2action[f"click({text}, {bounds_text})"] = line
                    continue

            alt_match = re.search(r'description="([^"]+)"', line)
            if alt_match:
                alt = alt_match.group(1).strip()
                if alt and alt != ' ':
                    icons.append(f"click({alt}, {bounds_text})")
                    html2action[f"click({alt}, {bounds_text})"] = line
                    continue

        # 处理可滚动元素
        if 'scrollable="true"' in line:
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
                scroll_actions = [
                    f"scroll({bounds_text},up)",
                    f"scroll({bounds_text},down)",
                    f"scroll({bounds_text},left)",
                    f"scroll({bounds_text},right)"
                ]
                bounds.extend(scroll_actions)
                for action in scroll_actions:
                    html2action[action] = bounds_text

    # 生成action space
    return icons, inputs, bounds, html2action





def box_actions_generate(html, xml):
    # 初始化列表
    inputs = []
    icons = []
    bounds = []
    anytree_root = parse_xml_to_anytree(xml)
    new_html = any_tree_to_html(anytree_root, 0, None)
    # 分割HTML内容为逐行处理
    lines1 = html.strip().split('\n')
    lines2 = new_html.strip().split('\n')
    html2action = {}

    # 遍历每一行HTML
    for line, line2 in zip(lines1, lines2):
        # 处理输入框
        count = 1
        if '<input' in line:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line)
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line2)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
            if text_match:  # 确保找到匹配项
                text = text_match.group(1)
            else:
                text = None
            if text:
                if text != ' ':
                    inputs.append(f"input(带有文本<ref>{text}</ref>的输入框, <box>{bounds_text}</box>)")
                    html2action[f"带有文本<ref>{text}</ref>的输入框, <box>{bounds_text}</box>"] = line
                    continue
                else:
                    inputs.append(f"input(第{count}个空白输入框, <box>{bounds_text}</box>)")
                    html2action[f"第{count}个空白输入框, <box>{bounds_text}</box>"] = line
                    count += 1
                    continue

        # 处理可点击元素
        if 'clickable="true"' in line:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line)
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line2)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
            if text_match:
                text = text_match.group(1).strip()
                if text and text != ' ':
                    icons.append(f"click(<ref>{text}</ref><box>{bounds_text}</box>)")
                    html2action[f"click(<ref>{text}</ref><box>{bounds_text}</box>)"] = line

                    continue

            alt_match = re.search(r'description="([^"]+)"', line)
            if alt_match:
                alt = alt_match.group(1).strip()
                if alt and alt != ' ':
                    icons.append(f"click(<ref>{alt}</ref><box>{bounds_text}</box>)")
                    html2action[f"click(<ref>{alt}</ref><box>{bounds_text}</box>)"] = line
                    continue

        # 处理可滚动元素
        if 'scrollable="true"' in line:
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
                scroll_actions = [
                    f"scroll(<box>{bounds_text}</box>,up)",
                    f"scroll(<box>{bounds_text}</box>,down)",
                    f"scroll(<box>{bounds_text}</box>,left)",
                    f"scroll(<box>{bounds_text}</box>,right)"
                ]
                bounds.extend(scroll_actions)
                for action in scroll_actions:
                    html2action[action] = bounds_text

    # 生成action space
    return icons, inputs, bounds, html2action


def infer_original_bounds_and_direction(start_coords, end_coords):
    # 计算中点坐标
    mid_x = (start_coords[0] + end_coords[0]) // 2
    mid_y = (start_coords[1] + end_coords[1]) // 2

    # 计算偏移量
    offset_x = abs(start_coords[0] - end_coords[0]) // 2
    offset_y = abs(start_coords[1] - end_coords[1]) // 2

    # 推断滚动方向
    if start_coords[1] < end_coords[1]:  # 垂直向上滚动
        direction = 'down'
    elif start_coords[1] > end_coords[1]:  # 垂直向下滚动
        direction = 'up'
    elif start_coords[0] < end_coords[0]:  # 水平向左滚动
        direction = 'left'
    else:  # 水平向右滚动
        direction = 'right'

    # 回推原始坐标bounds
    if direction in ['up', 'down']:
        x1 = mid_x - offset_x * 2
        x2 = mid_x + offset_x * 2
        y1 = mid_y - offset_y
        y2 = mid_y + offset_y
    else:
        x1 = mid_x - offset_x
        x2 = mid_x + offset_x
        y1 = mid_y - offset_y * 2
        y2 = mid_y + offset_y * 2

    return f'[{x1},{y1}][{x2},{y2}]', direction


def dict_scroll_parameters(bounds, direction):
    match = re.search(r'\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\]', bounds)
    bounds = [match.group(1), match.group(2)]
    # 解析bounds字符串"[x1,y1][x2,y2]"
    x1, y1 = map(int, bounds[0].split(','))
    x2, y2 = map(int, bounds[1].split(','))

    # 计算中点坐标
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2

    # 定义滚动偏移量
    offset_x = (x2 - x1) // 4
    offset_y = (y2 - y1) // 4

    # 根据方向计算滚动起始和结束坐标
    scroll_directions = {
        'up': ([mid_x,mid_y + offset_y], [mid_x,mid_y - offset_y]),
        'down': ([mid_x,mid_y - offset_y], [mid_x,mid_y + offset_y]),
        'left': ([mid_x + offset_x,mid_y], [mid_x - offset_x,mid_y]),
        'right': ([mid_x - offset_x,mid_y], [mid_x + offset_x,mid_y])
    }

    return scroll_directions[direction]

def process_action(answer, scroll, html2action):  # 将实际指令转化为模型输入的格式
    parts = answer.split('(', 1)
    action = parts[0].strip().lower()  # Action: click, scroll, input
    params = parts[1].rstrip(')').split(',') if len(parts) > 1 else []
    if action == 'click':
        action_command = 'click'
        text_match = re.search(r'>\s*([^<>]+)\s*<', answer)
        if text_match:
            # text = text_match.group(1).strip()
            # params_command = text
            # return f"{action_command}({params_command})"
            for key, value in html2action.items():
                if value == params[0]:
                    return f"{key}"

        alt_match = re.search(r'description="([^"]+)"', answer)
        if alt_match:
            # alt = alt_match.group(1).strip()
            # params_command = alt
            # return f"{action_command}({params_command})"
            for key, value in html2action.items():
                if value == params[0]:
                    return f"{key}"
        return "click error"
    elif action == 'scroll':
        action_command = 'scroll'
        match = re.search(r'\[([0-9]+, [0-9]+)\], \[([0-9]+, [0-9]+)\]', answer)
        bounds = [match.group(1), match.group(2)]
        # 解析bounds字符串"[x1,y1][x2,y2]"
        x1, y1 = map(int, bounds[0].split(','))
        x2, y2 = map(int, bounds[1].split(','))
        # Defining scroll directions as start and end coordinates
        for item in scroll:
            match = re.search(r'scroll\(\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\],(\w+)\)', item)
            if match:
                bound = f'[{match.group(1)}][{match.group(2)}]'
                direction = match.group(3)
                params_command = calculate_scroll_parameters(bound, direction)
                # print(f"([{x1}, {y1}), [{x2}, {y2}])")
                # print(params_command)
                coords = params_command
                formatted_coords = f"([{coords[0][0]}, {coords[0][1]}), [{coords[1][0]}, {coords[1][1]}])"
                # print(formatted_coords)
                if f"([{x1}, {y1}), [{x2}, {y2}])" == formatted_coords:
                    return item
        return "scroll error"

    elif action == 'input':
        action_command = 'input'
        text_match = re.search(r'>\s*([^<>]+)\s*<', answer)
        if text_match:
            text = text_match.group(1)
            if text != ' ':
                for key, value in html2action.items():
                    if value == params[0]:
                        return f"{action_command}({key}, {params[1]})"
            else:
                for key, value in html2action.items():
                    if value == params[0]:
                        return f"{action_command}({key}, {params[1]})"
                return "input error"
        else:
            return "input error"
        
def process_user_input(user_input, elements_map):  # 将模型输入转化为实际的执行指令
    # Splitting the input for action and parameters
    parts = user_input.split('(', 1)
    action = parts[0].strip().lower()  # Action: click, scroll, input
    # Defining the action command and parameters
    action_command = ''
    params_command = ''
    # Determine the action and construct corresponding command
    if action == 'click':
        action_command = 'click'
        if user_input in elements_map:
            params_command = elements_map[user_input]
            final_command = f"{params_command}"

            return final_command
        else:
            return "click:模型输入转化为实际输入失败"
    elif action == 'scroll':
        action_command = 'scroll'
        # Defining scroll directions as start and end coordinates
        match = re.search(r'scroll\(\[([0-9]+,[0-9]+)\]\[([0-9]+,[0-9]+)\],(\w+)\)', user_input)
        if match:
            bounds = f'[{match.group(1)}][{match.group(2)}]'
            direction = match.group(3)
            params_command = calculate_scroll_parameters(bounds, direction)
            final_command = f"{action_command}{params_command}"
            return final_command
        else:
            return "scroll:模型输入转化为实际输入失败"
    elif action == 'input':
        action_command = 'input'
        params = parts[1].rstrip(')').split(', ') if len(parts) > 1 else []  # Parameters in the parentheses
        if params and params[0] in elements_map:
            params_command = elements_map[params[0]]
            if len(params) > 1:
                params_command += "," + f"{params[1]}"

    # Construct the final command
    final_command = f"{action_command}({params_command})"

    return final_command


# def judge_acton2html(action, html):



def format_description(inputs, icons):
    # 描述输入框
    inputs_desc = f"该页面包含以下输入框：{'，'.join(inputs)}。" if inputs else "该页面没有输入框。"

    # 描述可点击元素
    icons_desc = f"可点击的控件包括：{'，'.join(icons)}。" if icons else "此页面上没有可点击的控件。"


    # 组合所有描述
    full_description = f"{inputs_desc}{icons_desc}"
    return full_description

def sample_elements(inputs, icons):
    cleaned_inputs = [item for item in inputs if item.strip()]
    cleaned_icons = [item for item in icons if item.strip()]

    # Combine the cleaned lists
    combined_list = cleaned_inputs + cleaned_icons
    # combined_list = inputs + icons
    number = random.randint(1, 5)
    # If the combined list is smaller than the required number of samples, return the whole list
    if len(combined_list) <= number:
        return combined_list

    # Otherwise, randomly sample 'number' elements from the combined list
    return random.sample(combined_list, number)



def generate_query():
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path):
            # 构造当前级别和上一级目录的HTML文件名
            current_html_filename = f"{subdir}-html.txt"
            parent_prefix = '_'.join(subdir.split('_')[:-1])
            parent_html_filename = f"{parent_prefix}-html.txt"

            # 构造完整的文件路径
            current_html_path = os.path.join(subdir_path, current_html_filename)
            parent_html_path = os.path.join(subdir_path, parent_html_filename)

            # 检查并读取当前级别的HTML文件
            if os.path.exists(current_html_path):
                with open(current_html_path, 'r', encoding='utf-8') as file:
                    current_html_content = file.read()
                inputs2, icons2, bounds2 = process_html(current_html_content)

            # 检查并读取上一级目录的HTML文件
            if os.path.exists(parent_html_path):
                with open(parent_html_path, 'r', encoding='utf-8') as file:
                    parent_html_content = file.read()
                icons1, inputs1, bounds1, _ = actions_generate(parent_html_content)

            # 生成输入数据
            input1 = generate_task1_input(html2text(icons2, inputs2, bounds2), random.choice(page_description_instruction))

            # # 为生成 input2 数据，从 inputs2 和 icons2 中采样元素
            input2 = generate_task2_input(html2text(icons1, inputs1, bounds1), random.choice(next_page_action_instruction).format(
                next_icons=', '.join(sample_elements(icons2, inputs2))))
            input_txt_path = os.path.join(subdir_path, f"{subdir}-input.txt")

            # 将input2的结果写入到-input.txt文件
            with open(input_txt_path, 'w', encoding='utf-8') as output_file:
                output_file.write(input2)
                print(f"Saved input1 to {input_txt_path}")



def print_tree(node, depth=0):
    indent = " " * (depth * 2)
    if node.is_leaf:
        return f"{indent}{node.name}"
    else:
        children = ', '.join(print_tree(child, depth + 1) for child in node.children)
        return f"{indent}{node.name} ({children})"

def any_tree_to_html(node, layer, clickable_label):
    """Turns an AnyTree representation of view hierarchy into HTML.
    Args:
    node: an AnyTree node.
    layer: which layer is the node in.

    Returns:
    results: output HTML.
    """
    results = ''
    if 'ImageView' in node.type:
        node_type = 'img'
    elif 'IconView' in node.type:
        node_type = 'img'
    elif 'Button' in node.type:
        node_type = 'button'
    elif 'Image' in node.type:
        node_type = 'img'
    elif 'MenuItemView' in node.type:
        node_type = 'button'
    elif 'EditText' in node.type:
        node_type = 'input'
    elif 'TextView' in node.type:
        node_type = 'p'
    else:
        node_type = 'div'

    if node.clickable == "true":
        clickable_label = "true"
    elif clickable_label == "true":
        node.clickable = "true"
    if node.text:
        node.text = node.text.replace('\n', '')
    if node.content_desc:
        node.content_desc = node.content_desc.replace('\n', '')

    #  or node.class_label == 'android.widget.EditText'
    if node.is_leaf and node.visible:
        html_close_tag = node_type
        if node.scrollable == "true":
            html_close_tag = node_type
            results = '<{}{}{}{}{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id="{}"'.format(node.resource_id)
                if node.resource_id
                else '',
                ' package="{}"'.format(node.package)
                if node.package
                else '',

                ' class="{}"'.format(''.join(node.class_label))
                if node.class_label
                else '',
                ' description="{}"'.format(node.content_desc) if node.content_desc else '',
                ' clickable="{}"'.format(node.clickable) if node.clickable else '',
                ' scrollable="{}"'.format(node.scrollable) if node.scrollable else '',
                ' bounds="{}"'.format(node.bounds) if node.bounds else '',
                '{}'.format(node.text) if node.text else '',
                html_close_tag,
            )
        else:
            results = '<{}{}{}{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id="{}"'.format(node.resource_id)
                if node.resource_id
                else '',
                ' package="{}"'.format(node.package)
                if node.package
                else '',

                ' class="{}"'.format(''.join(node.class_label))
                if node.class_label
                else '',

                ' description="{}"'.format(node.content_desc) if node.content_desc else '',
                ' clickable="{}"'.format(node.clickable) if node.clickable else '',
                ' bounds="{}"'.format(node.bounds) if node.bounds else '',
                '{}'.format(node.text) if node.text else '',
                html_close_tag,
            )

    else:
        if node.scrollable == "true":
            html_close_tag = node_type
            results = '<{}{}{}{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id="{}"'.format(node.resource_id)
                if node.resource_id
                else '',

                ' class="{}"'.format(''.join(node.class_label))
                if node.class_label
                else '',

                ' descript  ion="{}"'.format(node.content_desc) if node.content_desc else '',
                ' clickable="{}"'.format(node.clickable) if node.clickable else '',
                ' scrollable="{}"'.format(node.scrollable) if node.scrollable else '',
                ' bounds="{}"'.format(node.bounds) if node.bounds else '',

                '{}'.format(node.text) if node.text else '',
                html_close_tag,
            )
        for child in node.children:
            results += any_tree_to_html(child, layer + 1, clickable_label)

    return results




def build_dict(xml, html):
    # 初始化列表
    keys = []
    anytree_root = parse_xml_to_anytree(xml)
    new_html = any_tree_to_html(anytree_root, 0, None)
    # 分割HTML内容为逐行处理
    lines1 = html.strip().split('\n')
    lines2 = new_html.strip().split('\n')
    html2action = {}
    # 遍历每一行HTML
    for line1, line2 in zip(lines1, lines2):
        # 处理输入框
        count = 1
        if '<input' in line1:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line1)
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line2)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
            if text_match:  # 确保找到匹配项
                text = text_match.group(1)
            else:
                text = None
            if text and bounds_text:
                if text != ' ' and line1 not in html2action:
                    html2action[line1] = [f"带有文本{text}的输入框", bounds_text]
                    continue
                else:
                    if line1 not in html2action:
                        html2action[line1] = [f"第{count}个空白输入框", bounds_text]
                        count += 1
                        continue
        # 处理可点击元素
        if 'clickable=' in line1:
            text_match = re.search(r'>\s*([^<>]+)\s*<', line1)
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line2)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
            if text_match:
                text = text_match.group(1).strip()
                if text and text != ' ' and line1 not in html2action:
                    html2action[line1] = [text, bounds_text]
                    continue
            alt_match = re.search(r'description="([^"]+)"', line1)
            if alt_match:
                alt = alt_match.group(1).strip()
                bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line2)
                if bounds_match:  # 确保找到匹配项
                    bounds_text = bounds_match.group(1).strip()
                if alt and alt != ' ' and line1 not in html2action:
                    html2action[line1] = [alt, bounds_text]
                    continue
        # 处理可滚动元素
        if 'scrollable="true"' in line1:
            bounds_match = re.search(r'bounds="(\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\])"', line1)
            if bounds_match:  # 确保找到匹配项
                bounds_text = bounds_match.group(1).strip()
                if bounds_text and line1 not in html2action:
                    html2action[line1] = [' ', bounds_text]
    return html2action

def display_image_with_annotations(image_path, bounds, label):
    # 打开图像文件
    image = Image.open(image_path)
    fig, ax = plt.subplots()

    # 显示图像
    ax.imshow(image)

    # 解析bounds字符串 "[x1,y1][x2,y2]"
    bounds = bounds.strip('[]')
    x1, y1, x2, y2 = map(int, bounds.replace('][', ',').split(','))

    # 计算矩形的宽度和高度
    width = x2 - x1
    height = y2 - y1

    # 创建一个矩形patch
    rect = patches.Rectangle((x1, y1), width, height, linewidth=2, edgecolor='r', facecolor='none')

    # 添加矩形到图像中
    ax.add_patch(rect)

    # 添加文本标注
    # ax.text(x1, y1 - 10, label, fontsize=12, color='red', verticalalignment='top', horizontalalignment='center')

    # 显示图像和标注
    plt.show()


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

def print_tree_with_text_and_bounds(node, depth=0):
    if 'ImageView' in node.type:
        node.type = 'IMAGE'
    elif 'IconView' in node.type:
        node.type = 'IMAGE'
    elif 'Button' in node.type:
        node.type = 'BUTTON'
    elif 'Image' in node.type:
        node.type = 'IMAGE'
    elif 'MenuItemView' in node.type:
        node.type = 'BUTTON'
    elif 'EditText' in node.type:
        node.type = 'INPUT'
    elif 'TextView' in node.type:
        node.type = 'P'
    else:
        node.type = 'DIV'
    result = ""
    # 只有当节点的 text 属性不为空时才处理
    if True:
        bounds = node.bounds if node.bounds else "No Bounds"
        if node.text != '' and node.bounds:
            result = f"{node.type} - {node.text} {bounds}"
        else:
            result = ''

        # 如果该节点有子节点，递归调用此函数并在结果中加入括号
        child_results = []
        for child in node.children:
            child_result = print_tree_with_text_and_bounds(child, depth + 1)
            if child_result:  # 只添加有结果的子节点
                child_results.append(child_result)

        if child_results:
            result += " (" + ", ".join(child_results) + ")"
    return result

def print_text_and_bounds(node, depth=0):
    result = ""
    # 只有当节点的 text 属性不为空时才处理
    if True:
        bounds = node.bounds if node.bounds else "No Bounds"
        if node.text != '' and node.bounds:
            result = f"<ref>{node.text}</ref><box>{bounds}</box>"
        else:
            result = ''

        # 如果该节点有子节点，递归调用此函数并在结果中加入括号
        child_results = []
        for child in node.children:
            child_result = print_text_and_bounds(child, depth + 1)
            if child_result:  # 只添加有结果的子节点
                child_results.append(child_result)

        if child_results:
            result += "\n".join(child_results)
    return result



def generate_task1_input():
    # 任务1 描述页面结构
    instruction=random.choice(page_structure_instruction)
    return instruction

def generate_task1_OCR_output(xml):
    anytree_root = parse_xml_to_anytree(xml)
    if anytree_root:
        text = print_text_and_bounds(anytree_root)
        return text
    else:
        return 'xml error'


def generate_task1_output(xml):
    anytree_root = parse_xml_to_anytree(xml)
    if anytree_root:
        text = print_tree_with_text_and_bounds(anytree_root)
        flag = True
        text = text[1:]
        while flag:
            if text.startswith("( ") and text.endswith(")"):
                text = text[2:-1]
                flag = True
            else:
                flag = False # flag = True
            # text = text[1:]
            # while flag:
            #     if text.startswith("( ") and text.endswith(")"):
            #         text = text[2:-1]
            #         flag = True
            #     else:
            #         flag = False
        return text
    else:
        return 'xml error'

def generate_task4_input():
    """
       4. 屏幕总结-整体(Caption)
       """
    instruction=random.choice(page_description_instruction)
    return f"\n{instruction}"


def generate_task5_input():
    """
       5. 屏幕跳转action生成 （Two Image Navigation）
       """
    instruction=random.choice(next_page_action_instruction)
    return f"\n{instruction}"

def generate_task2_input():
    """
      2. 屏幕action space生成
       """
    instruction=random.choice(page_action_space_instruction)
    return f"\n{instruction}"
def generate_task2_output(html):
    """
       2. 屏幕action space生成
       """
    res = actions_generate(html)
    return res

def generate_task3_REF_input(html, xml, instruction=random.choice(icon_location_instruction)):
    """
       3. 屏幕物体定位-单个（以VQA形式询问text）(REC)
       返回 output error即为生成错误
       """
    # re.sub(r'\xa0', ' ', html)
    lines1 = html.strip().split('\n')
    length = len(lines1)
    text2bounds = build_dict(xml, html)
    line = random.choice(lines1)
    text_match = re.search(r'>\s*([^<>]+)\s*<', line)
    alt_match = re.search(r'description="([^"]+)"', line)
    if text_match:
        key = text_match.group(1).strip()
        if alt_match and key == '':
            key = alt_match.group(1).strip()
    else:
        return "output error", "output error"
    count = 1
    while key == '' and count < length:
        line = random.choice(lines1)
        count += 1
        text_match = re.search(r'>\s*([^<>]+)\s*<', line)
        alt_match = re.search(r'description="([^"]+)"', line)
        if text_match:
            key = text_match.group(1).strip()
            if alt_match and key == '':
                key = alt_match.group(1).strip()
        else:
            continue
    if count >= length:
        return "output error", "output error"
    try:
        text = text2bounds[line][0].strip()
    except KeyError:
        # 如果line不是字典的键，执行这里的代码
        return "output error", "output error"
    res = instruction.format(text=text)
    ans = f'<ref>{text}</ref><box>{text2bounds[line][1]}</box>'
    return res, ans


def generate_task3_input(html, xml, instruction=random.choice(icon_location_instruction)):
    """
       3. 屏幕物体定位-单个（以VQA形式询问text）(REC)
       返回 output error即为生成错误
       """
    # re.sub(r'\xa0', ' ', html)
    lines1 = html.strip().split('\n')
    length = len(lines1)
    text2bounds = build_dict(xml, html)
    line = random.choice(lines1)
    text_match = re.search(r'>\s*([^<>]+)\s*<', line)
    alt_match = re.search(r'description="([^"]+)"', line)
    if text_match:
        key = text_match.group(1).strip()
        if alt_match and key == '':
            key = alt_match.group(1).strip()
    else:
        return "output error", "output error"
    count = 1
    while key == '' and count < length:
        line = random.choice(lines1)
        count += 1
        text_match = re.search(r'>\s*([^<>]+)\s*<', line)
        alt_match = re.search(r'description="([^"]+)"', line)
        if text_match:
            key = text_match.group(1).strip()
            if alt_match and key == '':
                key = alt_match.group(1).strip()
        else:
            continue
    if count >= length:
        return "output error", "output error"
    try:
        text = text2bounds[line][0].strip()
    except KeyError:
        # 如果line不是字典的键，执行这里的代码
        return "output error", "output error"
    res = instruction.format(text=text)
    ans = f'{text}, {text2bounds[line][1]}'
    return res, ans


def html2text(icons, inputs, bounds):
    if icons == [] and inputs == [] and icons == []:
        return "html error"
    else:
        return f"可点击控件有\n" + "\n".join(icons) + "\n可输入控件有\n" + "\n".join(inputs) + "\n可滚动控件有\n" + "\n".join(bounds) 


if __name__ == "__main__":
    # image_path = 'ctrip0_0_844_1980_784_8496_8647-screen.png'
    # html1_path = 'dumpsys_output.txt'
    # html2_path = 'html.txt'
    # with open(html1_path, 'r', encoding='utf-8') as file:
    #     xml_content = file.read()
    # with open(html2_path, 'r', encoding='utf-8') as file:
    #     html2_content = file.read()
    # click = 'click(<div package="com.qq.reader" class="android.view.View" description="免费" clickable="true">  </div>)'
    # input = 'input(<input package="ctrip.android.view" class="android.widget.EditText" clickable="true"> 100 </input>,xwk)'
    # dict = build_dict(xml_content, html2_content)
    # print(dict)
    # draw = dict['<p package="ctrip.android.view" class="android.widget.TextView" clickable="true"> 广州塔 </p>']
    # print(draw[0], draw[1])
    # display_image_with_annotations(image_path, draw[1], draw[0])
    # task5
    # for i in range(1, 5):
    #     task5_input = generate_task5_input()
    #     print(task5_input)

    # # task4
    # task4_input = generate_task4_input()
    # print(task4_input)
    # # task2
    # task2_input = generate_task2_input()
    # print(task2_input)
    # # output
    # icons, inputs, bounds, html2action = actions_generate(html2_content, xml_content)
    # print(process_action(click, bounds, html2action))
    # print(process_action(input, bounds, html2action))
    # print(html2text(icons, inputs, bounds))
    # task3
    # q, ans = generate_task3_input(html2_content, xml_content)
    # print(q)
    # # output
    # print(ans)
    # anytree_root = parse_xml_to_anytree(xml_content)
    # text = print_tree_with_text_and_bounds(anytree_root)

    # print(text)
    # print(generate_task1_input())
    # print(generate_task1_output(xml_content))

    # # task ref 的input，output生成
    # root_dir = '/home/corpus/test_515/few_shot/example'
    # for subdir in os.listdir(root_dir):
    #     subdir_path = os.path.join(root_dir, subdir)
    #     print(subdir_path)
    #     if os.path.isdir(subdir_path):
    #         current_html_filename = f"{subdir}-html.txt"
    #         current_xml_filename = f"{subdir}-xml.txt"
    #         current_html_path = os.path.join(subdir_path, current_html_filename)
    #         current_xml_path = os.path.join(subdir_path, current_xml_filename)
    #         if os.path.exists(current_html_path):
    #             with open(current_html_path, 'r', encoding='utf-8') as file:
    #                 current_html_content = file.read()
    #             with open(current_xml_path, 'r', encoding='utf-8') as file:
    #                 current_xml_content = file.read()
    #             q, ans = generate_task3_REF_input(current_html_content, current_xml_content)
    #             count = 0 
    #             while q == 'output error' and ans == 'output error' and count <= 10:
    #                 q, ans = generate_task3_REF_input(current_html_content, current_xml_content)
    #                 count += 1
    #             print(q, ans)
    #             input_txt_path = os.path.join(subdir_path, f"{subdir}-refinput.txt")
    #             output_txt_path = os.path.join(subdir_path, f"{subdir}-refoutput.txt")
    #             with open(input_txt_path, 'w', encoding='utf-8') as output_file:
    #                 output_file.write(q)
    #             with open(output_txt_path, 'w', encoding='utf-8') as output_file:
    #                 output_file.write(ans)   
                # # 
                # 
                # 
    
    # # ask actionspace 的的input，output生成
    # root_dir = '/home/corpus/test_515/few_shot/example'
    # for subdir in os.listdir(root_dir):
    #     subdir_path = os.path.join(root_dir, subdir)
    #     if os.path.isdir(subdir_path):
    #         current_html_filename = f"{subdir}-html.txt"
    #         current_xml_filename = f"{subdir}-xml.txt"
    #         current_html_path = os.path.join(subdir_path, current_html_filename)
    #         current_xml_path = os.path.join(subdir_path, current_xml_filename)
    #         if os.path.exists(current_html_path):
    #             with open(current_html_path, 'r', encoding='utf-8') as file:
    #                 current_html_content = file.read()
    #             with open(current_xml_path, 'r', encoding='utf-8') as file:
    #                 current_xml_content = file.read()
    #             icons, inputs, bounds, html2action = box_actions_generate(current_html_content, current_xml_content)
    #             q = generate_task2_input()
    #             ans = html2text(icons, inputs, bounds)
    #             print(q, ans)
    #             input_txt_path = os.path.join(subdir_path, f"{subdir}-actionspaceinput.txt")
    #             output_txt_path = os.path.join(subdir_path, f"{subdir}-actionspaceoutput.txt")
    #             with open(input_txt_path, 'w', encoding='utf-8') as output_file:
    #                 output_file.write(q)
    #             with open(output_txt_path, 'w', encoding='utf-8') as output_file:
    #                 output_file.write(ans)   
    #             # os.remove(input_txt_path) 
    #             # os.remove(output_txt_path) 
    

    # OCR 的的input，output生成
    root_dir = '/home/corpus/test_515/few_shot/example'
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path):
            current_html_filename = f"{subdir}-html.txt"
            current_xml_filename = f"{subdir}-xml.txt"
            current_html_path = os.path.join(subdir_path, current_html_filename)
            current_xml_path = os.path.join(subdir_path, current_xml_filename)
            if os.path.exists(current_html_path):
                with open(current_html_path, 'r', encoding='utf-8') as file:
                    current_html_content = file.read()
                with open(current_xml_path, 'r', encoding='utf-8') as file:
                    current_xml_content = file.read()
                icons, inputs, bounds, html2action = box_actions_generate(current_html_content, current_xml_content)
                q = generate_task1_input()
                ans = generate_task1_OCR_output(current_xml_content)
                print(q, ans)
                input_txt_path = os.path.join(subdir_path, f"{subdir}-ocrinput.txt")
                output_txt_path = os.path.join(subdir_path, f"{subdir}-ocroutput.txt")
                with open(input_txt_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(q)
                with open(output_txt_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(ans)   
                # os.remove(input_txt_path)
                # os.remove(output_txt_path)


    # # task navigation 的input output生成
    # root_dir = '/home/corpus/test_515/test_data/unseen_data/navigation_test'
    # count = 0 
    # for subdir in os.listdir(root_dir):
    #     subdir_path = os.path.join(root_dir, subdir)
    #     if os.path.isdir(subdir_path):
    #         # 构造当前级别和上一级目录的HTML文件名
    #         current_html_filename = f"{subdir}-html.txt"
    #         parent_prefix = '_'.join(subdir.split('_')[:-1])
    #         parent_html_filename = f"{parent_prefix}-html.txt"
    #         current_json_filename = f"{subdir}.json"
    #         current_xml_filename = f"{subdir}-xml.txt"
    #         parent_xml_filename = f"{parent_prefix}-xml.txt"
    
    #         # 构造完整的文件路径
    #         current_html_path = os.path.join(subdir_path, current_html_filename)
    #         parent_html_path = os.path.join(subdir_path, parent_html_filename)
    #         current_json_path = os.path.join(subdir_path, current_json_filename)
    #         current_xml_path = os.path.join(subdir_path, current_xml_filename)
    #         parent_xml_path = os.path.join(subdir_path, parent_xml_filename)
    
    #         # 检查并读取当前级别的HTML文件
    #         if os.path.exists(current_html_path):
    #             with open(current_html_path, 'r', encoding='utf-8') as file:
    #                 current_html_content = file.read()
    #             with open(current_xml_path, 'r', encoding='utf-8') as file:
    #                 current_xml_content = file.read()
    #             inputs2, icons2, bounds2 = process_html(current_html_content)
    
    #         # 检查并读取上一级目录的HTML文件
    #         if os.path.exists(parent_html_path):
    #             with open(parent_html_path, 'r', encoding='utf-8') as file:
    #                 parent_html_content = file.read()
    #             with open(parent_xml_path, 'r', encoding='utf-8') as file:
    #                 parent_xml_content = file.read()
    #             icons1, inputs1, bounds1, _ = box_actions_generate(parent_html_content, parent_xml_content)
    
    #         # # 为生成 input2 数据，从 inputs2 和 icons2 中采样元素
    #         # input2 = generate_task5_input(next_icons=', '.join(sample_elements(icons2, inputs2)))
    #         input2 = generate_task5_input()
    #         input_txt_path = os.path.join(subdir_path, f"{subdir}-input.txt")
    #         output_txt_path = os.path.join(subdir_path, f"{subdir}-output.txt")
    #         if os.path.exists(output_txt_path):
    #             continue
    #         with open(current_json_path, 'r', encoding='utf-8') as file:
    #                 current_json_content = json.load(file)
    #         output_origin = current_json_content['history_actions'][-1]
    #         # print(output_origin)
    #         icons, inputs, bounds, html2action = box_actions_generate(current_html_content, current_xml_content)
    #         output = process_action(output_origin, bounds, html2action)
    #         # print(input2, output)
    #         if not output:
    #             print(output)
    #             shutil.rmtree(subdir_path) 
    #             count += 1
    #             continue
    #         elif "error" in output:
    #             print(output)
    #             count += 1
    #             shutil.rmtree(subdir_path)
    #             continue
    #         # 将input2的结果写入到-input.txt文件
    #         with open(input_txt_path, 'w', encoding='utf-8') as output_file:
    #             output_file.write(input2)
    #         with open(output_txt_path, 'w', encoding='utf-8') as output_file:
    #             output_file.write(output)   
    # print(count)
