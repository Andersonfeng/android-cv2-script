from time import sleep
import os
import cv2
import numpy
import threading
import sys


parent_path = './simulator/' 
threshold = 0.8 # 匹配精确度
semaphore = threading.Semaphore(3) # 最大线程数
sleep_time = 1 #配置需要sleep的时间
device_ip = '192.168.50.120:5555'
in_battle = False

def match_screenshot(target_path, template_path):
    target = cv2.imread(target_path)
    template = cv2.imread(template_path)
    theight, twidth = template.shape[:2]
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(sys._getframe().f_code.co_name, template_path, max_val, max_loc)
    return max_val > threshold, (max_loc[0]+twidth/2, max_loc[1]+theight/2)


def tap(x, y):    
    os.system('adb -s '+device_ip+' shell input tap {} {}'.format(x, y))
    global sleep_time
    sleep_time+=1


def swipe(x1, y1, x2, y2, time):
    print('开始滑动', x1, y1, x2, y2)
    os.system(
        'adb -s '+device_ip+' shell input swipe {} {} {} {} {}'.format(x1, y1, x2, y2, time))


def take_screen_shot(filename='screenshot'):  # 对手机进行截图并发送到电脑指定位置
    os.system(
        'adb -s '+device_ip+' shell /system/bin/screencap -p /sdcard/'+str(filename)+'.png')

    os.system(
        'adb -s '+device_ip+' pull /sdcard/'+str(filename)+'.png ./simulator/screenshot/'+str(filename)+'.png')
    return './simulator/screenshot/'+str(filename)+'.png'


def select_MOJIA_agency(target):
    print("开始选择墨家机关道")

    screenshot_list = ['battle', 'solo', 'ai_mode', 'mojiajiguandao', 'hero_list',
                       'mage', 'hero_zhugeliang', 'confirm',  'continue', 'return_to_hall', 'giveup', 'confirm_2','return_to_hall_fromtaozhuang']
    thread_list = []
    for filename in screenshot_list:
        file_ab_path = ""+parent_path+filename+'.png'
        thread = threading.Thread(target=multi_match_and_tap,args=(target, file_ab_path))
        thread_list.append(thread)
        thread.start()

        # for thread in thread_list:
        #     thread.join()
        # match, location = match_screenshot(target, file_ab_path)
        # if(match):
        #     tap(location[0], location[1])
        #     sleep(0.5)
            # target = take_screen_shot(sys._getframe().f_code.co_name)  # 点击之后截取下一个画面
    # target = take_screen_shot(sys._getframe().f_code.co_name)  # 点击之后截取下一个画面
    sleep(2)


def multi_match_and_tap(target,template): #多线程匹配截图和点击
    with semaphore:
        match, location = match_screenshot(target, template)
        if(match):
            print("===match===",target,template,"tap",location[0], location[1])
            tap(location[0], location[1])

def move_action(target):
    print("开始无尽向前")

    tp = ""+parent_path+'tp.png'
    match, location = match_screenshot(target, tp)
    tp_dead = ""+parent_path+'tp-dead.png'
    # match2, location2 = match_screenshot(target, tp_dead)
    # match = match | match2

    count = 0
    threading.Thread(target=detect_enemy,args=()).start()
    threading.Thread(target=detect_enemy,args=()).start()
    while(in_battle):

        swipe(400, 1300, 800, 700, 1000)
        # swipe(400, 1300, 0, 1900, 1000)
        sleep(0.2)
        count += 1
        if(count % 5 == 0):
            target = take_screen_shot(sys._getframe().f_code.co_name)
            match, location = match_screenshot(target, tp_dead)

def detect_battle(): # 检测是否还在战斗状态
    return

def detect_enemy(): #检测敌人是否存在 , 需要单独一条线程去run
    global in_battle
    while(in_battle):
        target = take_screen_shot(sys._getframe().f_code.co_name)
        enemy_healthbar = ""+parent_path+'enemy_healthbar.png'
        print('detect_enemy',match_screenshot(target, enemy_healthbar))

def team_match(target):
    # 长平攻防战
    '''
    实现长平攻防战自动战斗
    第一步 进入游戏:对战 -> 3v3长平攻防战 -> 人机-> 开始匹配 -> 确认 -> 英雄列表 -> 鲁班7号 -> 确认

    第二步 战斗: 关闭技能介绍 -> 加技能 -> 发现红色血条放技能 平A -> 自己绿色血条过半后退 ->掉血点击恢复 -> 防御塔标志发光时攻击防御塔

    第三部 回到大厅 : 继续->继续->返回大厅->确定->下次吧->确定
    '''

    enter_game = ['battle', '3v3_team_match', 'ai_mode', 'start_match', 'confirm_match', 'hero_list',
                  'shooter', 'hero_luban7hao', 'confirm']

    battle_list = ['upgrade_skill.png', 'upgrade_skill_2.png',
                   'luban_skill_1.png', 'luban_skill_3.png', 'attack.png', 'attack_tower', 'continue']

    back_to_hall = ['continue', 'return_to_hall',
                    'giveup', 'confirm_2', 'battle']

    flag = True
    unmatch_count = 0
    while(flag):
        for filename in enter_game:
            file_ab_path = ""+parent_path+filename+'.png'
            match, location = match_screenshot(target, file_ab_path)
            if(match):
                tap(location[0], location[1])
                target = take_screen_shot(
                    sys._getframe().f_code.co_name)  # 点击之后截取下一个画面

                if(filename == 'confirm'):  # 如果选择了英雄并点击确定 就跳出循环选择战斗
                    flag = False
                    break
            else:
                unmatch_count += 1
                if(unmatch_count > 2*len(enter_game)):  # 匹配n轮都匹配不上就退出循环
                    flag = False
                    break

    '''
        战斗系统怎么改进呢
    '''
    flag = True
    unmatch_count = 0
    while(flag):
        for filename in battle_list:
            file_ab_path = ""+parent_path+filename+'.png'
            match, location = match_screenshot(target, file_ab_path)
            if(match):
                tap(location[0], location[1])
                target = take_screen_shot(
                    sys._getframe().f_code.co_name)  # 点击之后截取下一个画面

                if(filename == 'continue'):  # 屏幕出现继续就跳出战斗循环
                    flag = False
                    break
            else:
                unmatch_count += 1
                if(unmatch_count > 2*len(battle_list)):  # 匹配n轮都匹配不上就退出循环
                    flag = False
                    break

    flag = True
    unmatch_count = 0
    while(flag):
        for filename in back_to_hall:
            file_ab_path = ""+parent_path+filename+'.png'
            match, location = match_screenshot(target, file_ab_path)
            if(match):
                if(filename == "battle"):  # 检测到对战按钮说明回到大厅了,跳出循环
                    flag = False
                    break
                tap(location[0], location[1])
                target = take_screen_shot(
                    sys._getframe().f_code.co_name)  # 点击之后截取下一个画面
            else:
                unmatch_count += 1
                if(unmatch_count > 2*len(back_to_hall)):  # 匹配n轮都匹配不上就退出循环
                    flag = False
                    break

    return


def battle(target):
    '''
    模拟与人机对战
    主要规则: 
        当技能升级出现时点击升级技能 : 一二技能 三技能
        当自己血条过半时撤退:绿色血条过半撤退并点击恢复技能,直到血条回到3/4,回到战斗
        发现红色血条放技能1+2+3+平A
        当有防御塔攻击提示时优先攻击防御塔    
    '''
    battle_list = ['upgrade_skill', 'upgrade_skill_2',
                   'luban_skill_1', 'luban_skill_3', 'attack', 'attack_tower', 'enemy_healthbar','continue']
    count=0
    while (True):
        for filename in battle_list:
            swipe(400, 1300, 800, 700, 5000)
            file_ab_path = ""+parent_path+filename+'.png'
            match, location = match_screenshot(target, file_ab_path)
            if(match):
                tap(location[0], location[1])
                target = take_screen_shot(
                    sys._getframe().f_code.co_name)  # 点击之后截取下一个画面
                continue

                if(filename == 'continue'):  # 屏幕出现继续就跳出战斗循环
                    flag = False
                    break
        count+=1
        target = take_screen_shot(
                        sys._getframe().f_code.co_name+str(count))
                   

def init_adb():
    # os.system('adb.exe kill-server')
    # os.system('adb.exe start-server')
    print(os.system('adb.exe connect '+device_ip))
    # print(os.system('adb.exe devices'))


def run():
    global sleep_time
    count = 0
    while (True):
        count+=1
        target = take_screen_shot(sys._getframe().f_code.co_name+str(count%10))
        # team_match(target)
        # battle(target)
        select_MOJIA_agency(target)
        move_action(target)
        sleep(sleep_time)
        sleep_time = 1


# take_screen_shot()
init_adb()
run()
# threading.Thread(target=take_screen_shot).start()
# threading.Thread(target=select_MOJIA_agency).start()
# threading.Thread(target=move_action).start()

'''
#todo 每个图片给一个线程去匹配
#todo 考虑是否接入scrcpy实现多点触控
'''