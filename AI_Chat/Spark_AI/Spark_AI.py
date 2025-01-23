# -*- coding: utf-8 -*-
# @Time    : 2025/1/19 15:11
# @Author  : HeLong
# @FileName: Spark_AI.py
# @Software: PyCharm
# AI接口，从服务端获取数据
import os
import sys

from AI_Chat.Spark_AI import SparkApi
import json

def read_config(file_path):
    config = {}
    with open(file_path, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config

def get_config():
    config_file_path = os.path.join(os.path.dirname(__file__), '..', '.Sparkconfig')
    config = read_config(config_file_path)
    return config['appID'], config['apiKey'], config['apiSecret']

def get_text(role, content):
    return {"role": role, "content": content}

def check_length(text, max_length=8000):
    current_length = sum(len(item["content"]) for item in text)
    if current_length > max_length:
        text.pop(0)  # Remove the oldest message if the length exceeds the limit
    return text

def text_division(text_input):
    appid, api_key, api_secret = get_config()
    domain = "lite"  # Lite
    Spark_url = "wss://spark-api.xf-yun.com/v1.1/chat"  # Lite Server

    text = [
        {
        "role": "system",
        "content": """
         你是一个文本分类器，负责将用户输入的问题划分为 **操作指令（D）** 和 **问答内容（Q）**。请按以下规则处理：

         ### 分类规则
         1. **操作指令（D）**  
            - 包含明确动作（如“检查”“打开”“巡查”等）  
            - 描述需要执行的具体任务（如“调节温度”“关闭灯光”）

         2. **问答内容（Q）**  
            - 包含疑问词（如“什么”“如何”“是否”“为什么”）  
            - 需要知识检索或信息回答的问题（如天气、新闻、解释类问题）

         ### 输出格式
         - 用 `D = "..."` 和 `Q = "..."` 严格分隔，每条内容用数字序号标注  
         - **若某一类别无内容，则设为 `NULL`**（例如只有操作指令时，Q = NULL）  
         - 忽略无法分类的内容

         ### 示例
         输入：巡查卧室，检查室内是否安全。明天的天气怎么样？今天有什么热点？  
         输出：  
         D = "1.巡查卧室 2.检查室内是否安全"  
         Q = "1.明天的天气怎么样？ 2.今天有什么热点？"

         输入：帮我关灯  
         输出：  
         D = "1.帮我关灯"  
         Q = NULL

         输入：今天北京有雨吗？  
         输出：  
         D = NULL  
         Q = "1.今天北京有雨吗？"

         ---

         ### 现在请处理用户输入：
         
         """
        }
        # Set up work requirements
    ]

    # user_input = input("\n我: ")
    # question = check_length(text + [get_text("user", user_input)])
    question = check_length(text + [get_text("user", text_input)])
    SparkApi.answer = ""
    print("星火: ", end="")
    try:
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        print("The API call is successful")
    except Exception as e:
        print(f"An error occurred: {e}")
    return SparkApi.answer

def ai_reply(user_input):
    # Request Massages
    appid, api_key, api_secret = get_config()
    domain = "generalv3.5"
    spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"
    text = [

    ]
    # user_input = input("\nMe")
    question = check_length(text + [get_text("user", user_input)])
    SparkApi.answer = ""
    print("Reply: ", end="")
    try:
        SparkApi.main(appid, api_key, api_secret, spark_url, domain, question)
        print("The API call is successful")
    except Exception as e:
        print(f"An error occurred: {e}")
    return SparkApi.answer

# if __name__ == "__main__":
#     a = text_division("巡查卧室，检查室内是否安全。明天的天气怎么样？今天有什么热点？")
#     print(a)