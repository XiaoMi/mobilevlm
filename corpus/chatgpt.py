#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
import requests
import os
import openai
import backoff
import requests

completion_tokens = prompt_tokens = 0

# if api_key != "":
#     openai.api_key = api_key
# else:
#     print("Warning: OPENAI_API_KEY is not set")
#
# api_base = os.getenv("OPENAI_API_BASE", "https://api.aiguoguo199.com/v1")
# if api_base != "":
#     print("Warning: OPENAI_API_BASE is set to {}".format(api_base))
#     openai.api_base = api_base
#
#
# # @backoff.on_exception(backoff.expo)
# # def completions_with_backoff(**kwargs):
# #     return openai.ChatCompletion.create(**kwargs)
# def chatgpt(prompt):
#     """
#
#     """
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             # {'role': 'system', 'content': persona},
#             {'role': 'user', 'content': prompt}
#         ],
#         temperature=0.1,
#         max_tokens=1000,
#         n=1,
#         stop=None,
#         top_p=0.95
#         )
#     print("response: ", response)
#     return response

# def gpt(prompt, model="gpt-3.5-turbo", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
#     # 使用GPT模型生成对话，返回生成的消息列表
#     messages = [{"role": "user", "content": prompt}]
#     return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)


# def chatgpt(messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
#     global completion_tokens, prompt_tokens
#     outputs = []
#     while n > 0:
#         # 限制每次请求的数量，以避免出现请求过多的情况
#         cnt = min(n, 20)
#         n -= cnt
#         # 使用backoff算法重试生成对话请求，返回生成的消息列表
#         res = completions_with_backoff(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens,
#                                        n=cnt, stop=stop)
#         '''
#         res是一个字典，包含从GPT模型返回的响应信息。res["choices"]是一个列表，其中包含GPT模型生成的若干个响应。每个响应是一个字典，包含以下键：
#         "text"：一个字符串，表示GPT模型生成的响应文本。
#         "finish_reason"：一个字符串，表示GPT模型停止生成响应的原因。
#         "index"：一个整数，表示GPT模型生成响应的索引。
#         "logprobs"：一个字典，表示GPT模型生成响应时的对数概率。
#         "tokens"：一个列表，表示GPT模型生成响应时使用的令牌（标记）序列。
#         "message"：一个字典，包含以下键：
#             "content"：一个字符串，表示GPT模型生成的响应文本。
#             "metadata"：一个字典，包含与响应相关的元数据。
#         '''
#         outputs.extend([choice["message"]["content"] for choice in res["choices"]])
#         # log completion tokens
#         # 记录使用的生成响应和接受提示使用的token数。
#         completion_tokens += res["usage"]["completion_tokens"]
#         prompt_tokens += res["usage"]["prompt_tokens"]
#     return outputs

#######################  Xiaomi API接口  ##########################
def chatgpt(prompt, model="gpt-4", temperature=0.1, max_tokens=1000, n=1, stop=None) -> list:
    headers = {'Content-Type': 'application/json'}
    url = ''  # gpt-4/3.5 for ChatCompletion
    outputs = []
    cnt = min(n, 20)
    while n > 0:
        if model == "gpt-4":
            data = {"uid": "xx9ty", "prompt": prompt, "history": [], "model": "gpt-4-0314",
                    "max_tokens": max_tokens, "n": cnt, "temperature": temperature, "stop": stop}  # if n>1, response of data is a List.
        elif model == "gpt-3.5-turbo":
            data = {"uid": "xx9ty", "prompt": prompt, "history": [],
                    "max_tokens": max_tokens, "n": cnt, "temperature": temperature, "stop": stop}
        response = requests.post(url, json=data, headers=headers)
        try:
            res = response.json()
            if isinstance(res['response'], list):
                assert cnt > 1
                outputs.extend(res['response'])
            elif isinstance(res['response'], str):
                assert cnt == 1
                outputs.append(res['response'])
            else:
                print("None of outputs!")
            n -= cnt
            cnt = min(n, 20)
        except Exception as e:
            # print(e)
            pass
    # print(len(outputs))
    # for i, output in enumerate(outputs):
    #     print(i, output)
    # print("data", data)
    return outputs

def gpt_usage(backend="gpt-4"):
    # 根据使用的GPT模型计算使用的completion_tokens和prompt_tokens，并计算出费用
    global completion_tokens, prompt_tokens
    if backend == "gpt-4":
        cost = completion_tokens / 1000 * 0.06 + prompt_tokens / 1000 * 0.03
    elif backend == "gpt-3.5-turbo":
        cost = (completion_tokens + prompt_tokens) / 1000 * 0.0002
    return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}
