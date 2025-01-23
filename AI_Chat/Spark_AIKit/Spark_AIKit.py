# -*- coding: utf-8 -*-
# @Time    : 2025/1/19 13:44
# @Author  : HeLong
# @FileName: Spark_AIKit.py
# @Software: PyCharm
# @Blog    ：https://blog.duolaa.asia/
# Tips: It needs to be deployed on the Linux platform, and other platforms cannot call the debugging interface
import ctypes
import os
import re

from ctypes import c_char_p, c_int, c_void_p, POINTER, Structure
from AI_Chat.Spark_AI.Spark_AI import ai_reply, text_division
from AI_Chat.Speech_To_Text.Speech2Text import stt

# Read. Sparkconfig file
def read_config(file_path):
    config = {}
    with open(file_path, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key] = value
    return config

# Config file directory
config_file_path = os.path.join('../.Sparkconfig')

# Read Configuration
config = read_config(config_file_path)
appID = config['appID'].encode('utf-8')
apiKey = config['apiKey'].encode('utf-8')
apiSecret = config['apiSecret'].encode('utf-8')

# Load the SDK library
lib = ctypes.CDLL('./libs/libaikit.so')

# Define the callback function type
CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p)

# Define the callback function

def callback(handle, event_type, event_value):
    if event_type == 1:
        print("唤醒词识别成功")
        text = stt()
        print("识别到的文本：",text)
        text_split = text_division(text)

        pattern_a = r'Q\s*=\s*"([^"]*)"'
        pattern_b = r'D\s*=\s*"([^"]*)"'
        match_a = re.search(pattern_a, text_split)
        match_b = re.search(pattern_b, text_split)

        if match_a:
            print(match_a.group(1))
            answer = ai_reply(match_a.group(1))
            # 此处回答需要传递到文字转语音接口
        if match_b:
            print(match_b.group(1))
            # 此处需要将结果传递给操作控制逻辑
# Register the callback function
lib.AIKIT_RegisterAbilityCallback.argtypes = [c_char_p, CALLBACK_TYPE]
lib.AIKIT_RegisterAbilityCallback(b'awaken', CALLBACK_TYPE(callback))

# Initialize the SDK
class AIKIT_BizParam(Structure):
    _fields_ = [("appID", c_char_p),
                ("apiKey", c_char_p),
                ("apiSecret", c_char_p),
                ("workDir", c_char_p)]

param = AIKIT_BizParam(
    appID=appID,
    apiKey=apiKey,
    apiSecret=apiSecret,
    workDir=b'./resource'
)

lib.AIKIT_Init.argtypes = [POINTER(AIKIT_BizParam)]
lib.AIKIT_Init(param)

# Load the wake word configuration file
class AIKIT_CustomData(Structure):
    _fields_ = [("key", c_char_p),
                ("index", c_int),
                ("from", c_int),
                ("value", c_char_p),
                ("len", c_int),
                ("next", c_void_p),
                ("reserved", c_void_p)]

custom_data = AIKIT_CustomData(
    key=b'key_word',
    index=0,
    from_=0,  # AIKIT_DATA_PTR_PATH
    value=b'./resource/keyword.txt',
    len=len('./resource/keyword.txt'),
    next=None,
    reserved=None
)

lib.AIKIT_LoadData.argtypes = [c_char_p, POINTER(AIKIT_CustomData)]
lib.AIKIT_LoadData(b'awaken', custom_data)

# Specify the wake word file to use
indexs = (c_int * 1)(0)  # 个性化资源索引数组
lib.AIKIT_SpecifyDataSet.argtypes = [c_char_p, c_char_p, POINTER(c_int), c_int]
lib.AIKIT_SpecifyDataSet(b'awaken', b'key_word', indexs, 1)

# Create a competency session
class AIKIT_HANDLE(Structure):
    _fields_ = [("handle", ctypes.c_void_p)]

handle = AIKIT_HANDLE()

class AIKIT_ParamBuilder(Structure):
    _fields_ = []

param_builder = lib.AIKIT_ParamBuilder_create()
lib.AIKIT_ParamBuilder_param.argtypes = [POINTER(AIKIT_ParamBuilder), c_char_p, c_char_p, c_int]
lib.AIKIT_ParamBuilder_param(param_builder, b'wdec_param_nCmThreshold', b'0 0:999', 8)
lib.AIKIT_ParamBuilder_param(param_builder, b'gramLoad', b'true', 1)

lib.AIKIT_Start.argtypes = [c_char_p, POINTER(AIKIT_ParamBuilder), ctypes.c_void_p, POINTER(AIKIT_HANDLE)]
lib.AIKIT_Start(b'awaken', param_builder, None, handle)

# Feed audio data
def send_audio_data(audio_data):
    class AIKIT_InputData(Structure):
        _fields_ = [("data", c_char_p),
                    ("length", c_int)]

    input_data = AIKIT_InputData(
        data=audio_data,
        length=len(audio_data)
    )

    lib.AIKIT_Write.argtypes = [POINTER(AIKIT_HANDLE), POINTER(AIKIT_InputData)]
    lib.AIKIT_Write(handle, input_data)

# End the session
lib.AIKIT_End.argtypes = [POINTER(AIKIT_HANDLE)]
lib.AIKIT_End(handle)

# Deinitialize the SDK
lib.AIKIT_Uninit()


