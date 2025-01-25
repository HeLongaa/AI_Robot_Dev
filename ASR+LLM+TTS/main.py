# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 00:49
# @Author  : HeLong
# @FileName: main.py
# @Software: PyCharm
# @Blog    : https://helong.online/


import pyaudio
import wave
from aip import AipSpeech
import os
import pyttsx3
from Spark_Model import Api_Run
import config
from User_Purpose import user_purpose

class Wake_Up:
    def __init__(self, APP_ID, API_KEY, SECRET_KEY, file_path):
        self.APP_ID = APP_ID
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.file_path = file_path
        self.engine = pyttsx3.init()

    def text_to_speech(self, text):
        """"Text-to-speech with pyttsx3"""
        self.engine.say(text)
        self.engine.runAndWait()

    def record_sound(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 5

        p = pyaudio.PyAudio()

        default_input_index = p.get_default_input_device_info()["index"]

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=default_input_index,
                        frames_per_buffer=CHUNK)

        print("请说话...")
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("录音结束")
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(self.file_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

    def voice2text(self):
        client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        with open(self.file_path, 'rb') as fp:
            audio_data = fp.read()

        result = client.asr(audio_data, 'wav', 16000, {'dev_pid': 1536})
        return result.get('result', [''])[0] if result.get('result') else ''

    def del_file(self):
        try:
            os.remove(self.file_path)
            print(f"文件 {self.file_path} 已删除")
        except FileNotFoundError:
            print(f"文件 {self.file_path} 不存在")


def Run_Talk(APP_ID, API_KEY, SECRET_KEY, file_path):
    wk = Wake_Up(APP_ID, API_KEY, SECRET_KEY, file_path)
    while True:
        wk.record_sound()
        chat_message = wk.voice2text()
        print("识别结果:", chat_message)

        if '小文' in chat_message:  # 唤醒词检测
            wk.del_file()
            print("唤醒成功")
            wk.text_to_speech("我在，请问有何吩咐")

            while True:
                wk.record_sound()
                chat_message = wk.voice2text()
                print("识别结果:", chat_message)
                purpose = user_purpose(chat_message)
                print(purpose)
                if purpose != 'Qu':
                    # 机器人操作
                    print("操作")
                    break
                if '退出' in chat_message:
                    wk.text_to_speech("好的，已退出问答")
                    break
                query = wk.voice2text()
                print("用户请求:", query)
                # wk.text_to_speech("好的，请稍等")
                response = Api_Run(query)  # Get Api
                # print("AI回复:", response)
                wk.text_to_speech(response)
            break
        else:
            continue


if __name__ == '__main__':
    APP_ID = config.BaiduApi.APP_ID
    API_KEY = config.BaiduApi.API_KEY
    SECRET_KEY = config.BaiduApi.SECRET_KEY

    AUDIO_PATH = './data/recording.wav'

    os.makedirs(os.path.dirname(AUDIO_PATH), exist_ok=True)
    while True:
        Run_Talk(APP_ID, API_KEY, SECRET_KEY, AUDIO_PATH)