# -*- coding: utf-8 -*-
# @Time    : 2025/1/19 15:11
# @Author  : HeLong
# @FileName: Spark_AI.py
# @Software: PyCharm
import os
import SparkApi
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

def spark_ai():
    appid, api_key, api_secret = get_config()
    domain = "lite"  # Lite
    Spark_url = "wss://spark-api.xf-yun.com/v1.1/chat"  # Lite Server

    text = []
    while True:
        user_input = input("\n我: ")
        question = check_length(text + [get_text("user", user_input)])
        SparkApi.answer = ""
        print("星火: ", end="")
        try:
            SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
            answer = SparkApi.answer
            # print(answer)
            text.append(get_text("assistant", answer))
        except Exception as e:
            print(f"An error occurred: {e}")
        text = check_length(text)