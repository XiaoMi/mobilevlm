#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.      

from gpt import * 
response = gpt_4v_screenqa(f"回答下面的问题，尽量简短，不要说无关的内容。你是谁？")
predicted_answer = response['response']
print(predicted_answer)
