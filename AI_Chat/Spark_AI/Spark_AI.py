# -*- coding: utf-8 -*-
# @Time    : 2025/1/19 15:11
# @Author  : HeLong
# @FileName: Spark_AI.py
# @Software: PyCharm
# AI接口，从服务端获取数据
import os
from AI_Chat.Spark_AI import SparkApi


#<-----------------------------------------原SparkApi接口内容--------------------------------------------->
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import time
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websocket  # 使用websocket_client
answer = ""
sid = ''

class Ws_Param(object):
    # Initialize
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        # print(url)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws,one,two):
    print(" ")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, domain= ws.domain,question=ws.question))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    # print(time.time())
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        global sid
        sid = data["header"]["sid"]
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content,end ="")
        global answer
        answer += content
        # print(1)
        if status == 2:
            ws.close()

def gen_params(appid, domain,question):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {

            "chat": {
                "domain": domain,
                "temperature": 0.8,
                "max_tokens": 2048,
                "top_k": 5,

                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data

def get(appid, api_key, api_secret, Spark_url,domain, question):
    wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

#<-----------------------------------------Spark_AI内容--------------------------------------------->

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
        get(appid, api_key, api_secret, Spark_url, domain, question)
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
    # print("Reply: ", end="")
    try:
        get(appid, api_key, api_secret, spark_url, domain, question)
        print("The API call is successful")
    except Exception as e:
        print(f"An error occurred: {e}")
    return SparkApi.answer

if __name__ == "__main__":
    a = ai_reply("明天的天气怎么样？今天有什么热点？")
    print(a)