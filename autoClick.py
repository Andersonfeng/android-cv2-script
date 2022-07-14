import os
import time
import datetime

# adb = "adb.exe"

device_ip = '192.168.50.204:39425'

def init():
    os.system('adb connect '+device_ip)


def run():
    count = 0
    while(True):
        # os.system('adb -s '+device_ip+' shell input swipe 1000 1000 1000 900')  # 从下往上滑
        os.system('adb -s '+device_ip+' shell input  keyevent 25')  # 音量-
        time.sleep(2)
        os.system('adb -s '+device_ip+' shell input  keyevent 24')  # 音量+
        # os.system('adb -s '+device_ip+' shell input swipe 1000 1000 1000 1200')  # 从上往下滑
        count += 1
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'sleep 300',count)
        time.sleep(300)

init()
run()

# os.system('adb version')