import os
from time import thread_time
import cv2
import numpy
import sys
import pyautogui
from PIL import ImageGrab, Image


# 测试一下confidence , 怎么才能定位到截图 而不是原图裁图
# 为什么pyautogui 可以用template 匹配到用图片管理器打开的截图 ,而cv2 匹配不到template和截图


threshold = 0.8


def match_screenshot(target_path, template_path, confidence=0.8, limit=10000):

    target = cv2.imread(target_path,0)
    template = cv2.imread(template_path,0)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(sys._getframe().f_code.co_name, template_path, max_val, max_loc)

    # location = numpy.where(result >= threshold)
    # theight, twidth = template.shape[:2]

    # for pt in zip(*location[::-1]):
    #     cv2.rectangle(target, pt, (pt[0] + twidth, pt[1] + theight), (0, 255, 255), 2)
    
    # cv2.imshow('result',target)
    # cv2.waitKey(0)

    # return max_val > threshold, (max_loc[0]+twidth/2, max_loc[1]+theight/2)


def match_by_pyautogui(template_path, confidence=threshold):
    loc = pyautogui.locateOnScreen(template_path, confidence)
    if(loc):
        print(loc)
        # pyautogui.moveTo(loc[0], loc[1], duration=0.5)
    else:
        print('pyautogui not match')


def take_screen_shot(filename='screenshot'):  # 对手机进行截图并发送到电脑指定位置
    os.system(
        'adb.exe shell /system/bin/screencap -p /sdcard/'+str(filename)+'.png')

    os.system(
        'adb.exe pull /sdcard/'+str(filename)+'.png ./simulator/screenshot/'+str(filename)+'.png')
    return './simulator/screenshot/'+str(filename)+'.png'

def init_adb():
    # os.system('adb.exe kill-server')
    # os.system('adb.exe start-server')
    print(os.system('adb.exe connect 192.168.50.120'))
    print(os.system('adb.exe devices'))

target_path = './simulator/screenshot/target.png'
template_path = './simulator/mage.png'
match_screenshot(target_path, template_path)
# match_by_pyautogui(template_path)
# init_adb()
# take_screen_shot()

