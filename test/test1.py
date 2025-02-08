from gpiozero import RGBLED
from colorzero import Color
from time import sleep

colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan']


led = RGBLED(19, 17, 0)

# 调用循环函数
def makerobo_loop():
	while True:
		for col in colors:
			led.color = Color(col)
			sleep(0.5)
# 释放资源
def makerobo_destroy():
	led.close()

# 程序入口
if __name__ == "__main__":
	try:
		makerobo_loop()        # 调用循环函数
	except KeyboardInterrupt:  # 当按下Ctrl+C时，将执行destroy()子程序。
		makerobo_destroy()     # 释放资源
