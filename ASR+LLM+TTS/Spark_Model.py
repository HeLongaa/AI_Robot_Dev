# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 00:49
# @Author  : HeLong
# @FileName: Spark_Model.py
# @Software: PyCharm
# @Blog    : https://helong.online/

# coding: utf-8
"""
# Call the Spark model
"""
import SparkApi
import config


appid = config.SparkApi.appid
api_secret = config.SparkApi.api_secret
api_key = config.SparkApi.api_key
domain = config.SparkApi.domain
Spark_url = config.SparkApi.Spark_url

# Initial contextual content
text = [
     # {"role": "system", "content": "你是一个家庭助手，你每次最多只能回复150字。"}
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


def Api_Run(input):
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
