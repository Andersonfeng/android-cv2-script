from time import sleep
import os
import cv2
import numpy
import threading

# target = cv2.imread(
#     "C:/Users/fky/Desktop/simulator/match-interface.png")

template_list = [
    cv2.imread("C:/Users/fky/Desktop/simulator/continue.png"),
    cv2.imread("C:/Users/fky/Desktop/simulator/solo.png"),
    cv2.imread("C:/Users/fky/Desktop/simulator/battle.png"),
    cv2.imread("C:/Users/fky/Desktop/simulator/rank.png"),
    cv2.imread("C:/Users/fky/Desktop/simulator/challenge.png"),
    cv2.imread("C:/Users/fky/Desktop/simulator/quanmindianjing.png"),
]


key_map = {
    "battle": {'x': 700, 'y': 800},
    "solo": {'x': 1200, 'y': 600},
    "ai_mode": {'x': 1000, 'y': 600},
    "mojiajiguandao": {'x': 200, 'y': 600},
    "hero": {'x': 100, 'y': 200},
    "confirm": {'x': 1700, 'y': 1000},
    "continue": {'x': 1000, 'y': 1000},
    "return_to_hall": {'x': 800, 'y': 1000},
    'keep_move': {'x1': 300, 'y1': 800, 'x2': 500, 'y2': 500, 'time': 5000},
}

parent_path = 'C:/Users/fky/Desktop/simulator/'

screenshot_list = ['battle', 'solo',
                   'ai_mode', 'mojiajiguandao', 'hero', 'confirm']

threshold=0.8

def matchScreenshot(target_path,template_path):
    target = cv2.imread(target_path)
    template = cv2.imread(template_path)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_val > threshold

def select_MOJIA_agency():
    print("开始选择墨家机关道")
    parent_path = 'C:/Users/fky/Desktop/simulator/'
    global call_time
    while(True):
        for filename in screenshot_list:
            file_ab_path = ""+parent_path+filename+'.png'            
            if(matchScreenshot(take_screen_shot(),file_ab_path)):
                tap_by_keymap(filename)       
                sleep(2)
            else:
                print('not match')            
            
def tap_by_keymap(key_name):    
    tap(key_map.get(key_name).get('x'), key_map.get(key_name).get('y'))


def tap(x, y):
    x=x*720/1080
    y=y*720/1080
    os.system("adb -s emulator-5554 shell input tap {} {}".format(x, y))


def swipe(x1, y1, x2, y2, time):
    x1=x1*720/1080
    x2=x2*720/1080
    y1=y1*720/1080
    y2=y2*720/1080
    os.system("adb -s emulator-5554 shell input swipe {} {} {} {} {}".format(
        x1, y1, x2, y2, time))

def take_screen_shot():        
            os.system('adb -s emulator-5554 shell /system/bin/screencap -p /sdcard/screenshot.png ; ')
            os.system('adb pull /sdcard/screenshot.png "C:/Users/fky/Desktop/simulator/screenshot/screenshot.png"')# adb pull /sdcard/screenshot.png "C:/Users/fky/Desktop/simulator/screenshot/screenshot.png"')
            return "C:/Users/fky/Desktop/simulator/screenshot/screenshot.png"
        
def move_action():
    print("开始无尽向前")
    parent_path = 'C:/Users/fky/Desktop/simulator/'    
    file_ab_path = ""+parent_path+'attack.png'            
    target = take_screen_shot()
    template = cv2.imread(file_ab_path)        
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    while(True):
        swipe(300, 800, 500, 500, 5000)
        sleep(0.5)
        tap_by_keymap('continue')    


# threading.Thread(target=take_screen_shot).start()
# threading.Thread(target=select_MOJIA_agency).start()
threading.Thread(target=move_action).start()

# 要把match 包装一下
