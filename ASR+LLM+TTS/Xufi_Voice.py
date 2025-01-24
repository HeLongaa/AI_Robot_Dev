# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 00:49
# @Author  : HeLong
# @FileName: Xufi_Voice.py
# @Software: PyCharm
# @Blog    : https://helong.online/

"""
# Call the Spark speech synthesis API to convert text to optimized speech output
"""
from Spark_Model import appid,api_secret,api_key
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
import pyaudio
import wave


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):

    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "x4_lingfeizhe_emo", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}

    # Generate URLs
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # RFC-1123
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + "tts-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # hmac-sha256
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": "tts-api.xfyun.cn"
        }

        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # print('websocket url :', url)
        return url

# API calls
class Make_Sound(object):
    def __init__(self, output_pcm,output_wav,wsParam):
        self.output_pcm = output_pcm
        self.output_wav = output_wav
        self.wsParam = wsParam

    def on_message(self,ws, message):
        try:
            message =json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            print(message)
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                with open(self.output_pcm, 'ab') as f:
                    f.write(audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)



    def on_error(self,ws, error):
        print("### error:", error)


    def on_close(self,ws,*args):
        print("### closed ###")


    def on_open(self,ws):
        output_pcm = self.output_pcm
        wsParam = self.wsParam
        def run(*args):
            d = {"common": wsParam.CommonArgs,
                 "business": wsParam.BusinessArgs,
                 "data": wsParam.Data,
                 }
            d = json.dumps(d)
            print("------>开始发送文本数据")
            ws.send(d)
            if os.path.exists(output_pcm):
                os.remove(output_pcm)

        thread.start_new_thread(run, ())


    # .pcm To .wav
    def pcm_2_wav(self):

        with open(self.output_pcm, 'rb') as pcmfile:
            pcmdata = pcmfile.read()
        with wave.open(self.output_wav, 'wb') as wavfile:
            wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
            wavfile.writeframes(pcmdata)
        now_time2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print("转wav结束时间"+str(now_time2))

    # Open .wav
    def sound_out(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        wf = wave.open(self.output_wav, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK, )

        data = wf.readframes(CHUNK)

        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()


def Run_Voice(output_pcm,output_wav,text):
    wsParam = Ws_Param(APPID=appid,APISecret=api_secret,APIKey=api_key,Text=text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ms = Make_Sound(output_pcm, output_wav,wsParam)
    ws = websocket.WebSocketApp(wsUrl, on_message=ms.on_message, on_error=ms.on_error, on_close=ms.on_close)
    ws.on_open = ms.on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    # Text To .pcm
    ms.pcm_2_wav()

    ms.sound_out()
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print("播放完毕：" + str(now_time))

