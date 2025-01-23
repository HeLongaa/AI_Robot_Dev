# -*- coding: utf-8 -*-
# @Time    : 2025/1/19 14:24
# @Author  : HeLong
# @FileName: Speech2Text.py
# @Software: PyCharm
# @Blog    ：https://helong.online/

import numpy as np
import pyaudio
import whisper


# Retuen result of Text
def stt():
    # Import Whisper-Tiny Model
    model = whisper.load_model("tiny")

    # Initialize the microphone input
    RATE = 16000
    CHUNK = 1024

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
    stream.start_stream()

    print("开始实时语音识别，按 Ctrl+C 退出")

    try:
        while True:
            # Get data from MIC
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

            # Identify using the Whisper model
            result = model.transcribe(audio_data, fp16=False)
            print("实时转录：", result["text"])
    except KeyboardInterrupt:
        print("\n结束语音识别")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    return result
