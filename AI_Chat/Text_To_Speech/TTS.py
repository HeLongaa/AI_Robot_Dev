# -*- coding: utf-8 -*-
# @Time    : 2025/1/19 15:11
# @Author  : HeLong
# @FileName: Spark_AI.py
# @Software: PyCharm

import os
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import time
import queue
import re
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket
import edge_tts
import asyncio
from io import BytesIO
from pydub import AudioSegment
import simpleaudio as sa


# --------------------------- 流式TTS模块 ---------------------------
class StreamTTS:
    def __init__(self):
        self.text_buffer = ""
        self.play_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()
        self.voice = "zh-CN-XiaoxiaoNeural"
        self.sentence_end_chars = {'。', '！', '？', '；', '，', '.', '!', '?', ';', ','}
        self.running = True
        thread.start_new_thread(self._tts_worker, ())

    def _split_sentences(self, text):
        """智能分句逻辑"""
        sentences = []
        buffer = ""
        for char in text:
            buffer += char
            if char in self.sentence_end_chars:
                sentences.append(buffer.strip())
                buffer = ""
        if buffer:
            sentences.append(buffer.strip())
        return sentences

    async def _generate_audio(self, text):
        """生成语音音频"""
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            audio_data = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
            return AudioSegment.from_mp3(BytesIO(audio_data))
        except Exception as e:
            print(f"[TTS错误] {str(e)}")
            return None

    def _tts_worker(self):
        """后台TTS工作线程"""
        asyncio.set_event_loop(self.loop)
        while self.running:
            text = self.play_queue.get()
            if text is None: break

            # 智能分句处理
            sentences = self._split_sentences(text)
            for sentence in sentences:
                if not sentence: continue

                # 生成并播放音频
                audio = self.loop.run_until_complete(self._generate_audio(sentence))
                if audio:
                    self._play_audio(audio)

    def _play_audio(self, audio):
        """播放音频"""
        try:
            playback = sa.play_buffer(
                audio.raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate
            )
            playback.wait_done()
        except Exception as e:
            print(f"[播放错误] {str(e)}")

    def add_text(self, text):
        """添加要合成的文本"""
        self.play_queue.put(text)

    def shutdown(self):
        """关闭TTS系统"""
        self.running = False
        self.play_queue.put(None)


# 初始化全局TTS引擎
tts_engine = StreamTTS()


# --------------------------- 讯飞星火API模块 ---------------------------
class WsParam:
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode(), signature_origin.encode(), hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode()).decode()
        return f"{self.Spark_url}?{urlencode({'authorization': authorization, 'date': date, 'host': self.host})}"


def on_message(ws, message):
    global answer
    data = json.loads(message)
    if data['header']['code'] != 0:
        print(f"[API错误] {data}")
        ws.close()
    else:
        content = data["payload"]["choices"]["text"][0]["content"]
        status = data["payload"]["choices"]["status"]

        # 流式输出文本
        print(content, end="", flush=True)

        # 流式发送到TTS
        tts_engine.add_text(content)

        answer += content
        if status == 2:
            ws.close()


def on_error(ws, error):
    print(f"[连接错误] {error}")


def on_close(ws, *args):
    print("[连接关闭]")


def on_open(ws):
    def run(*args):
        data = json.dumps(gen_params(ws.appid, ws.domain, ws.question))
        ws.send(data)

    thread.start_new_thread(run, ())


def gen_params(appid, domain, question):
    return {
        "header": {"app_id": appid, "uid": "1234"},
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.8,
                "max_tokens": 2048,
                "top_k": 5,
                "auditing": "default"
            }
        },
        "payload": {"message": {"text": question}}
    }


def get(appid, api_key, api_secret, Spark_url, domain, question):
    wsParam = WsParam(appid, api_key, api_secret, Spark_url)
    ws = websocket.WebSocketApp(
        wsParam.create_url(),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.appid = appid
    ws.question = question
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# --------------------------- 应用模块 ---------------------------
def read_config(file_path):
    config = {}
    with open(file_path, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config


def get_config():
    config_file_path = os.path.join(os.path.dirname(__file__), '..', '.Sparkconfig')
    return read_config(config_file_path).values()


answer = ""


def get_text(role, content):
    return {"role": role, "content": content}


def check_length(text, max_length=8000):
    current_length = sum(len(item["content"]) for item in text)
    if current_length > max_length:
        text.pop(0)
    return text


def ai_reply(user_input):
    global answer
    answer = ""

    appid, api_key, api_secret = get_config()
    domain = "generalv3.5"
    spark_url = "wss://spark-api-xf-yun.com/v3.5/chat"

    text = [get_text("user", user_input)]
    question = check_length(text)

    try:
        get(appid, api_key, api_secret, spark_url, domain, question)
    except Exception as e:
        print(f"[系统错误] {str(e)}")
        return ""

    return answer


if __name__ == "__main__":
    # 测试用例
    def test_query(prompt):
        print("\n用户提问:", prompt)
        print("AI回复: ", end="")
        response = ai_reply(prompt)
        print("\n完整回复:", response)


    test_query("请用生动的方式介绍量子计算机的工作原理")
    test_query("用Python实现快速排序算法并详细解释")

    # 关闭TTS系统
    tts_engine.shutdown()