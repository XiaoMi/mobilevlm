#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.      
from mimetypes import guess_type
import base64
import requests


# def get_model_response(self, prompt: str, images: List[str] = None) -> (bool, str):
#         headers = {'Content-Type': 'application/json'}
#         url = ''  # gpt-4/3.5 for ChatCompletion
#         outputs = []
#         n = self.n
#         cnt = min(n, 20)
#         while n > 0:
#             if self.model == "gpt-3.5-turbo":
#                 data = {"uid": "xx9ty", "prompt": prompt, "history": [],
#                         "max_tokens": self.max_tokens, "n": cnt, "temperature": self.temperature}
#                 url += '19005'
#             elif self.model == "gpt-4":
#                 data = {"uid": "xx9ty", "prompt": prompt, "history": [], "model": "gpt-4-0314",
#                         "max_tokens": self.max_tokens, "n": cnt, "temperature": self.temperature}  # if n>1, response of data is a List.
#                 url += '19006'
#             elif self.model == "gpt-4-vision-preview":
#                 content = [
#                     {
#                         "type": "text",
#                         "text": prompt
#                     }
#                 ]
#                 for img in images:
#                     base64_img = encode_image(img)
#                     content.append({
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_img}"
#                         }
#                     })
#                 messages = [
#                     {
#                         "role": 'user',
#                         "content": content
#                     }
#                 ]
#                 data = {"uid": "xx9ty", "messages": messages, "model": "gpt-4-vision-preview",
#                         "max_tokens": self.max_tokens, "n": cnt, "temperature": self.temperature}
#                 url += '19007'
#             response = requests.post(url, json=data, headers=headers)
#             try:
#                 res = response.json()
#                 if isinstance(res['response'], list):
#                     assert cnt > 1
#                     outputs.extend(res['response'])
#                 elif isinstance(res['response'], str):
#                     assert cnt == 1
#                     outputs.append(res['response'])
#                 else:
#                     print("None of outputs!")
#                 n -= cnt
#                 cnt = min(n, 20)
#             except Exception as e:
#                 return False, "API ERROR"
#         print(outputs)
#         return True, outputs[0]



def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"


def gpt_4v_ref(text1, image_path1, ans1, text2, image_path2):
    data_url1 = local_image_to_data_url(image_path1)
    data_url2 = local_image_to_data_url(image_path2)
    messages = [
                    { "role": "system", "content": "你是一个非常好的图像助手。" },
                    { "role": "user", "content": [  
                        { 
                            "type": "text", 
                            "text": f"{text1}" 
                        },
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url1}"
                            }
                        }
                    ] },
                    {
                        "role": "assistant", "content": f"{ans1}"
                    },
                    { "role": "user", "content": [  
                    { 
                        "type": "text", 
                        "text": f"{text2}" 
                    },
                    { 
                        "type": "image_url",
                        "image_url": {
                            "url": f"{data_url2}"
                        }
                    }
                ] }  
                ]
    res = requests.post(
            'http://***/api/gpt-4v/***', 
            json={
                "messages": messages,
                "max_tokens": 100
            })
    return res.json()

def gpt_4v_actionspace(text1, image_path1, ans1, text2, image_path2):
    data_url1 = local_image_to_data_url(image_path1)
    data_url2 = local_image_to_data_url(image_path2)
    messages = [
                    { "role": "system", "content": "你是一个非常好的图像助手。" },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url1}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text1}" 
                        },
                    ] },
                    {
                        "role": "assistant", "content": f"{ans1}"
                    },
                    { "role": "user", "content": [  
                    
                    { 
                        "type": "image_url",
                        "image_url": {
                            "url": f"{data_url2}"
                        }
                    },
                    { 
                        "type": "text", 
                        "text": f"{text2}" 
                    },
                ] }  
                ]
    res = requests.post(
            'http://***/api/gpt-4v/***', 
            json={
                "messages": messages,
                "max_tokens": 100
            })
    return res.json()

def gpt_4v_screenqa(text1, image_path1 = None):
    # data_url1 = local_image_to_data_url(image_path1)
    messages = [
                    { "role": "system", "content": "你是一个非常好的图像助手。" },
                    { "role": "user", "content": [  
                        { 
                            "type": "text", 
                            "text": f"{text1}" 
                        },
                        # { 
                        #     "type": "image_url",
                        #     "image_url": {
                        #         "url": f"{data_url1}"
                        #     }
                        # }
                    ] }
                ]
    res = requests.post(
            'http://***/api/gpt-4v/***', 
            json={
                "messages": messages,
                "max_tokens": 100
            })
    return res.json()

def gpt_4v_ocr(text1, image_path1, ans1, text2, image_path2):
    data_url1 = local_image_to_data_url(image_path1)
    data_url2 = local_image_to_data_url(image_path2)
    messages = [
                    { "role": "system", "content": "你是一个非常好的图像助手。你需要告诉我页面中有哪些内容，用<ref></ref>标记，以及他们的坐标，用<box></box>标记。" },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url1}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text1}" 
                        },
                    ] },
                    {
                        "role": "assistant", "content": f"{ans1}"
                    },
                    { "role": "user", "content": [  
                        
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url2}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text2}" 
                        },
                    ] }
                ]
    res = requests.post(
            'http://***/api/gpt-4v/***', 
            json={
                "messages": messages,
                "max_tokens": 100
            })
    return res.json()

def gpt_4v_navigation(text1, image_path1, image_path2, ans1, text2, image_path3, image_path4, ans2, text3, image_path5, image_path6):
    data_url1 = local_image_to_data_url(image_path1)
    data_url2 = local_image_to_data_url(image_path2)
    data_url3 = local_image_to_data_url(image_path3)
    data_url4 = local_image_to_data_url(image_path4)
    data_url5 = local_image_to_data_url(image_path5)
    data_url6 = local_image_to_data_url(image_path6)
    messages = [
                    { "role": "system", "content": "你是一个非常好的图像助手。你需要告诉我什么动作可以从第一张图像导航到第二张图像，你有三种动作，click、input、scroll" },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url1}"
                            }
                        },
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url2}"
                            }                      
                        },
                        { 
                            "type": "text", 
                            "text": f"{text1}" 
                        },
                    ] },
                    {
                        "role": "assistant", "content": f"{ans1}"
                    },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url3}"
                            }
                        },
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url4}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text2}" 
                        },
                    ] },
                    {
                        "role": "assistant", "content": f"{ans2}"
                    },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url5}"
                            }
                        },
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url6}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text3}, 操作对象xx应用<ref>xx</ref>括起来, 检测框用<box>[x1, y1][x2, y2]</box>, 请参考历史的格式。" 
                        },
                ] }  
                ]
    res = requests.post(
            'http://***/api/gpt-4v/***', 
            json={
                "messages": messages,
                "max_tokens": 100
            })
    return res.json()

def gpt_4v_stage3_navigation(text1, image_path1, ans1, text2, image_path3, ans2, text3, image_path5, image_path6):
    data_url1 = local_image_to_data_url(image_path1)
    data_url3 = local_image_to_data_url(image_path3)
    data_url5 = local_image_to_data_url(image_path5)
    messages = [
                    { "role": "system", "content": "你是一个非常好的图像助手。你需要告诉我什么动作可以从第一张图像导航到第二张图像，你有三种动作，click、input、scroll" },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url1}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text1}" 
                        },
                    ] },
                    {
                        "role": "assistant", "content": f"{ans1}"
                    },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url3}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text2}" 
                        },
                    ] },
                    {
                        "role": "assistant", "content": f"{ans2}"
                    },
                    { "role": "user", "content": [  
                        { 
                            "type": "image_url",
                            "image_url": {
                                "url": f"{data_url5}"
                            }
                        },
                        { 
                            "type": "text", 
                            "text": f"{text3}, 操作对象xx应用<ref>xx</ref>括起来, 检测框用<box>[x1, y1][x2, y2]</box>, 请参考历史的格式。" 
                        },
                ] }  
                ]
    res = requests.post(
            'http://***/api/gpt-4v/***', 
            json={
                "messages": messages,
                "max_tokens": 100
            })
    return res.json()



if __name__ == "__main__":
    text1 = '找出“翻唱”在屏幕上的位置。'
    image_path1 = '/home/corpus/test_58/few_shot/ref/image2/image2.png'
    ans1 = '[494,187][546,223]'
    text2 = '如何定位到界面中的“城市精选”。你只需要告诉我它的检测框[x1,y1][x2,y2]即可。'
    image_path2 = '/home/corpus/test_58/few_shot/ref/image1/image1.png'
    res = gpt_4v(text1, image_path1, ans1, text2, image_path2)
    # print(res)
    print(res['response'])
    
