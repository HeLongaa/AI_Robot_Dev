# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 21:06
# @Author  : HeLong
# @FileName: User_Purpose.py
# @Software: PyCharm
# @Blog    : https://helong.online/

import config
import SparkApi

appid = config.SparkApi.appid
api_secret = config.SparkApi.api_secret
api_key = config.SparkApi.api_key

domain = config.SparkApi.domain
Spark_url = config.SparkApi.Spark_url

text = [
    {"role":"system", "content":"你是一个语义分割模型，你需要区别我给你的话是操作还是问答，如果是操作就输出Do，问答输出Qu"}
]

def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text


def user_purpose(input):
    # 这里是运行主函数
    try:
        question = checklen(getText("user", input))
        print(question)
        SparkApi.answer = ""
        print("星火:", end="")
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        # print(SparkApi.answer)
        # output = getText("assistant", SparkApi.answer)
        # return output[1]['content']
        return SparkApi.answer
    except Exception as e:
        print(e)