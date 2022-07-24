import os
import time 
import cv2
import numpy
import sys
import subprocess
# import pyautogui
from PIL import ImageGrab, Image
import threading
import logging



# 测试一下confidence , 怎么才能定位到截图 而不是原图裁图
# 为什么pyautogui 可以用template 匹配到用图片管理器打开的截图 ,而cv2 匹配不到template和截图
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("test test teset")
threshold = 0.8
parent_path = './simulator/'
device_ip = '192.168.50.119:5555'
sem = threading.Semaphore(5)

def match_screenshot(target_path, template_path, confidence=0.8, limit=10000):
    while True:
        target = cv2.imread(target_path,1)
        template = cv2.imread(template_path,1)
        try:
            result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(sys._getframe().f_code.co_name, template_path, max_val, max_loc)
        except:
            continue
            

    # location = numpy.where(result >= threshold)
    theight, twidth = template.shape[:2]

    # for pt in zip(*location[::-1]):
    # cv2.rectangle(target, max_loc, (max_loc[0] + twidth, max_loc[1] + theight), (0, 255, 255), 2)

    # cv2.imshow('result',target)
    # cv2.waitKey(0)

    # return max_val > threshold, (max_loc[0]+twidth/2, max_loc[1]+theight/2)


# def match_by_pyautogui(template_path, confidence=threshold):
#     loc = pyautogui.locateOnScreen(template_path, confidence)
#     if(loc):
#         print(loc)
#         # pyautogui.moveTo(loc[0], loc[1], duration=0.5)
#     else:
#         print('pyautogui not match')


def take_screen_shot(filename='screenshot'):  # 对手机进行截图并发送到电脑指定位置
    while True:
        os.system(
            'adb -s '+device_ip+' shell /system/bin/screencap -p /sdcard/'+str(filename)+'.png')

        os.system(
            'adb -s '+device_ip+' pull /sdcard/'+str(filename)+'.png ./simulator/screenshot/'+str(filename)+'.png')
        time.sleep(1)
    return './simulator/screenshot/'+str(filename)+'.png'


def init_adb():
    # os.system('adb.exe kill-server')
    # os.system('adb.exe start-server')
    print(os.system('adb.exe connect 192.168.50.120'))
    print(os.system('adb.exe devices'))


def multi_action():
    battle_list = ['upgrade_skill', 'upgrade_skill_2',
                   'luban_skill_1', 'luban_skill_3', 'attack', 'attack_tower', 'eneny_healthbar', 'continue']
    
    
    for battle in battle_list:
        threading.Thread(target=match_screenshot,args=(target_path,""+parent_path+battle+'.png')).start()
            # match_screenshot(target_path,""+parent_path+battle+'.png')

def out_of_mem_test(target_path):
    '''
    测试大量调用cv2.matchTemplate 是否会爆出内存异常
    '''
    while True:
        for root,ds,fs in os.walk('D:\\Projects\\Python\\android-simulator-script\\simulator\\screenshot'):        
            for f in fs:
                file_ab_path = ""+parent_path+'/screenshot/'+f
                # match_screenshot(target_path,file_ab_path)
                threading.Thread(target=match_screenshot,args=(target_path,file_ab_path)).start()
            time.sleep(0.1)
            

    return

def test_subprocess():
    
    SCRCPY_dir = 'D:\\Program Files\\scrcpy-win64-v1.24'    
    device_ip = '192.168.50.119:5555'
    ADB_bin = os.path.join(SCRCPY_dir,"adb")
    
    adb_push = subprocess.Popen(
            [ADB_bin,'-s'+device_ip,'push',
            os.path.join(SCRCPY_dir,'scrcpy-server'),
            '/data/local/tmp/'],            
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=SCRCPY_dir)

    adb_push.wait()
    logger.info('out:%s',adb_push.stdout.read())
    logger.info('err:%s',adb_push.stderr.read())

    logger.info('run 完拉')
    return

def test_array():
    arr=[]
    for i in range(20):
        arr.append(i)
    print(arr)
    print(arr[0:8])
    print(arr[8:])
    
        

target_path = './simulator/screenshot/screenshot.png'
template_path = './simulator/confirm.png'
# out_of_mem_test(template_path)
# multi_action()
# match_by_pyautogui(template_path)
# init_adb()
# take_screen_shot()
# test_subprocess()
# test_array()
print(1000//60)
# threading.Thread(target=take_screen_shot,args=()).start()
# threading.Thread(target=match_screenshot,args=(target_path, template_path)).start()