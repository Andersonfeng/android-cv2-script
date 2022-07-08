from time import sleep
import os
import cv2
import numpy
import threading
import sys

template_list = [
    cv2.imread("./simulator/continue.png"),
    cv2.imread("./simulator/solo.png"),
    cv2.imread("./simulator/battle.png"),
    cv2.imread("./simulator/rank.png"),
    cv2.imread("./simulator/challenge.png"),
    cv2.imread("./simulator/quanmindianjing.png"),
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
    "giveup": {'x': 750, 'y': 750},
}

parent_path = './simulator/'

screenshot_list = ['battle', 'solo',
                   'ai_mode', 'mojiajiguandao', 'hero', 'confirm', 'continue', 'return_to_hall', 'giveup']

threshold = 0.8


def match_screenshot(target_path, template_path):
    target = cv2.imread(target_path)
    template = cv2.imread(template_path)
    theight, twidth = template.shape[:2]
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(sys._getframe().f_code.co_name, template_path, max_val, max_loc)
    return max_val > threshold, (max_loc[0]+twidth/2, max_loc[1]+theight/2)


def tap_by_keymap(key_name):
    print('点击位置', key_name)
    tap(key_map.get(key_name).get('x'), key_map.get(key_name).get('y'))


def tap(x, y):
    print("tap",x,y)
    os.system("adb.exe shell input tap {} {}".format(x, y))


def swipe(x1, y1, x2, y2, time):
    print('开始滑动',x1,y1,x2,y2)
    os.system(
        "adb.exe shell input swipe {} {} {} {} {}".format(x1, y1, x2, y2, time))


def take_screen_shot(filename='screenshot'):  # 对手机进行截图并发送到电脑指定位置
    os.system(
        'adb.exe shell /system/bin/screencap -p /sdcard/'+str(filename)+'.png')

    os.system(
        'adb.exe pull /sdcard/'+str(filename)+' "./simulator/screenshot/'+str(filename)+'.png"')
    return './simulator/screenshot/'+str(filename)+'.png'


def select_MOJIA_agency():
    print("开始选择墨家机关道")
    flag = True
    unmatch_count = 0
    while flag:
        target = take_screen_shot(sys._getframe().f_code.co_name)
        for filename in screenshot_list:
            file_ab_path = ""+parent_path+filename+'.png'
            match, location = match_screenshot(target, file_ab_path)
            if(match):                
                tap(location[0], location[1])
                sleep(2)
                take_screen_shot(sys._getframe().f_code.co_name) # 点击之后截取下一个画面
                unmatch_count = 0
            else:
                unmatch_count += 1
                if(unmatch_count >= len(screenshot_list)):
                    flag = False


def move_action():
    print("开始无尽向前")
    file_ab_path = ""+parent_path+'tp.png'
    match, location = match_screenshot(take_screen_shot(sys._getframe().f_code.co_name), file_ab_path)
    count = 0
    while(match):
        
        swipe(400, 1300, 800, 700, 5000)
        sleep(0.2)
        count+=1
        if(count%5==0):
            match, location = match_screenshot(take_screen_shot(sys._getframe().f_code.co_name), file_ab_path)


def init_adb():
    # os.system('adb.exe kill-server')
    # os.system('adb.exe start-server')
    print(os.system('adb.exe connect 192.168.50.120'))
    print(os.system('adb.exe devices'))


def run():
    while (True):
        # todo 应该先截个图 匹配到再tap 再截图
        select_MOJIA_agency()
        move_action()


# take_screen_shot()
init_adb()
run()
# threading.Thread(target=take_screen_shot).start()
# threading.Thread(target=select_MOJIA_agency).start()
# threading.Thread(target=move_action).start()