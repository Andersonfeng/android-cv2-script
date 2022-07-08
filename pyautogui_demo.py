from pyautogui import confirm, sleep
import pyautogui
import os
import time

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


def select_MOJIA_agency():
    print("开始选择墨家机关道")
    for filename in screenshot_list:
        if pyautogui.locateOnScreen(""+parent_path+filename+'.png', confidence=0.6):
            tap_by_keymap(filename)
            if(filename == 'mojiajiguandao'):
                time.sleep(5)
            time.sleep(2)
    while(True):

        if pyautogui.locateOnScreen(""+parent_path+'attack.png', confidence=0.6):
            move_action()
        sleep(2)


def move_action():
    print("开始无尽向前")
    while(True):
        swipe(300, 800, 500, 500, 5000)
        time.sleep(0.5)
        if pyautogui.locateOnScreen(""+parent_path+'continue.png', confidence=0.6):
            print('检测到继续按钮')
            # 点击回到主界面
            break
    tap_by_keymap('continue')    

    # 检查一下是否回到了主界面
    while(True):
        time.sleep(2)
        if(pyautogui.locateOnScreen(""+parent_path+'return_to_hall.png', confidence=0.6)):
            tap_by_keymap('return_to_hall')
            break
        if pyautogui.locateOnScreen(""+parent_path+'battle.png', confidence=0.6):
            select_MOJIA_agency()
            break


def tap_by_keymap(key_name):
    tap(key_map.get(key_name).get('x'), key_map.get(key_name).get('y'))


def tap(x, y):
    os.system("adb -s emulator-5554  shell input tap {} {}".format(x, y))


def swipe(x1, y1, x2, y2, time):
    os.system("adb -s emulator-5554  shell input swipe {} {} {} {} {}".format(
        x1, y1, x2, y2, time))


def match_single():
    location = pyautogui.locateOnScreen(
        "C:/Users/fky/Desktop/simulator/continue.png", confidence=0.6)
    print(location)


# select_MOJIA_agency()
# match_single()
# move_action()
# tap_by_keymap('continue')
def test():
    image_list = [
        pyautogui.locateOnScreen('C:/Users/fky/Desktop/simulator/continue.png', confidence=0.6),
        pyautogui.locateOnScreen('C:/Users/fky/Desktop/simulator/solo.png', confidence=0.6),
        pyautogui.locateOnScreen('C:/Users/fky/Desktop/simulator/battle.png', confidence=0.6),
        pyautogui.locateOnScreen('C:/Users/fky/Desktop/simulator/rank.png', confidence=0.6),
        pyautogui.locateOnScreen('C:/Users/fky/Desktop/simulator/challenge.png', confidence=0.6),
        pyautogui.locateOnScreen('C:/Users/fky/Desktop/simulator/quanmindianjing.png', confidence=0.6),
    ]
    for image in image_list:
        print(image)
    
test()

# adb shell /system/bin/screencap  -p /sdcard/screenshot.png ; adb pull /sdcard/screenshot.png "C:\Users\fky\Desktop\simulator\screenshot"


def take_screen_shot():
        return