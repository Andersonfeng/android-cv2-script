from time import sleep
import os
import cv2
import numpy
import threading
import sys
import queue


parent_path = './simulator/'
threshold = 0.8  # 匹配精确度
semaphore = threading.Semaphore(3)  # 最大线程数
device_ip = '192.168.50.119:5555'
in_battle = False
enemy_detect = False
target_path = './simulator/screenshot/screenshot_0.png'
current_target_path = './simulator/screenshot/screenshot_0.png'
skill_1 = [1800, 1400]
skill_2 = [2000, 1100]
skill_3 = [2200, 1000]
attack = [2200, 1400]

tap_queue = queue.Queue()


def consumer_queue():
    print('开始消费点击队列')
    while True:
        fun = tap_queue.get()
        fun()
        sleep(0.1)


def match_screenshot(target_path=current_target_path, template_path=''):
    global current_target_path
    target_path = current_target_path
    target = cv2.imread(target_path)
    template = cv2.imread(template_path)
    theight, twidth = template.shape[:2]
    try:
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if(max_val > threshold):
            print(sys._getframe().f_code.co_name,target_path,
                  template_path, round(max_val, 2), max_loc)
        return max_val > threshold, (max_loc[0]+twidth/2, max_loc[1]+theight/2)
    except Exception as e:
        print('出现异常:', e)
        return False, None


def tap(x, y):
    os.system('adb -s '+device_ip+' shell input tap {} {}'.format(x, y))


def swipe(x1, y1, x2, y2, time):
    print('开始滑动', x1, y1, x2, y2)
    os.system(
        'adb -s '+device_ip+' shell input swipe {} {} {} {} {}'.format(x1, y1, x2, y2, time))


def take_screen_shot(filename='screenshot'):  # 对手机进行截图并发送到电脑指定位置
    global current_target_path
    count = 0
    while True:
        count += 1
        current_file_name = filename+'_'+str(count % 2)  #截图为n个 , 这样匹配图片时不会发生读取错误
        os.system(
            'adb -s '+device_ip+' shell /system/bin/screencap -p /sdcard/'+str(current_file_name)+'.png')

        os.system(
            'adb -s '+device_ip+' pull /sdcard/'+str(current_file_name)+'.png ./simulator/screenshot/'+str(current_file_name)+'.png')
        current_target_path = './simulator/screenshot/'+current_file_name+'.png'
        sleep(1)


def select_MOJIA_agency():
    print("开始选择墨家机关道")

    screenshot_list = ['battle', 'solo', 'ai_mode', 'mojiajiguandao', 'hero_list',
                       'mage', 'hero_zhugeliang', 'confirm',  'continue', 'return_to_hall', 'giveup', 'confirm_2', 'return_to_hall_fromtaozhuang']

    while True:
        if(in_battle == False):
            for filename in screenshot_list:
                file_ab_path = ""+parent_path+filename+'.png'
                match, location = match_screenshot(target_path, file_ab_path)
                if(match):
                    tap_queue.put(lambda: tap(location[0], location[1]))
                    # target = take_screen_shot(sys._getframe().f_code.co_name)
        sleep(1)
            # target = take_screen_shot(sys._getframe().f_code.co_name)


def move_action():

    global in_battle
    print("开始无尽向前")

    while True:
        if(in_battle):
            swipe(400, 1300, 800, 700, 1000)


def detect_battle():  # 检测是否还在战斗状态
    print('开始检测战斗')
    global in_battle

    while True:
        tp = ""+parent_path+'tp.png'
        tp_dead = ""+parent_path+'tp-dead.png'
        # target = take_screen_shot(sys._getframe().f_code.co_name)
        tp, location = match_screenshot(target_path, tp)
        tp_dead, location = match_screenshot(target_path, tp_dead)
        in_battle = tp | tp_dead

        if(in_battle != True):
            print("not in battle now")
            sleep(5)
        sleep(1)


def detect_enemy():  # 检测敌人是否存在 , 需要单独一条线程去run
    print('开始检测敌人')
    global in_battle
    global enemy_detect

    while(True):
        if(in_battle):
            # target = take_screen_shot(sys._getframe().f_code.co_name)
            enemy_healthbar = ""+parent_path+'enemy_healthbar.png'
            upgrade_skill_2 = ""+parent_path+'upgrade_skill_2.png'
            upgrade_skill = ""+parent_path+'upgrade_skill.png'
            # upgrade_skill_2
            enemy_detect, location = match_screenshot(target_path, enemy_healthbar)
            upgrade_skill_2, upgrade_skill_2_location = match_screenshot(target_path, upgrade_skill_2)
            if(upgrade_skill_2):
                tap_queue.put(lambda: tap(upgrade_skill_2_location[0], upgrade_skill_2_location[1]))
            upgrade_skill, upgrade_skill_location = match_screenshot(target_path, upgrade_skill)
            if(upgrade_skill):
                tap_queue.put(lambda: tap(upgrade_skill_location[0], upgrade_skill_location[1]))

            # if(enemy):
            #     print('检测到敌人!!!', )
            #     tap_queue.put(lambda: tap(skill_1[0], skill_1[1]))
            #     tap_queue.put(lambda: tap(skill_2[0], skill_2[1]))
            #     tap_queue.put(lambda: tap(skill_3[0], skill_3[1]))
            #     tap_queue.put(lambda: tap(attack[0], attack[1]))
            sleep(1)
        sleep(1)

def attack_enemy():
    global enemy_detect
    while True:
        if(in_battle and enemy_detect):
            print('检测到敌人!!!')
            swipe(400, 1300, 0, 1900, 1000)
            tap_queue.put(lambda: tap(skill_1[0], skill_1[1]))
            tap_queue.put(lambda: tap(skill_2[0], skill_2[1]))
            tap_queue.put(lambda: tap(skill_3[0], skill_3[1]))
            tap_queue.put(lambda: tap(attack[0], attack[1]))

            sleep(1)
        sleep(1)


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
            match, location = match_screenshot(target_path, file_ab_path)
            if(match):
                tap(location[0], location[1])
                # target = take_screen_shot(
                #     sys._getframe().f_code.co_name)  # 点击之后截取下一个画面

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
            match, location = match_screenshot(target_path, file_ab_path)
            if(match):
                tap(location[0], location[1])
                # target = take_screen_shot(
                #     sys._getframe().f_code.co_name)  # 点击之后截取下一个画面

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
            match, location = match_screenshot(target_path, file_ab_path)
            if(match):
                if(filename == "battle"):  # 检测到对战按钮说明回到大厅了,跳出循环
                    flag = False
                    break
                tap(location[0], location[1])
                # target = take_screen_shot(                    sys._getframe().f_code.co_name)  # 点击之后截取下一个画面
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
                   'luban_skill_1', 'luban_skill_3', 'attack', 'attack_tower', 'enemy_healthbar', 'continue']
    count = 0
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
        count += 1
        target = take_screen_shot(
            sys._getframe().f_code.co_name+str(count))


def init_adb():
    # os.system('adb.exe kill-server')
    # os.system('adb.exe start-server')
    print(os.system('adb.exe connect '+device_ip))
    # print(os.system('adb.exe devices'))


def run():
    threading.Thread(target=take_screen_shot, args=()).start()
    threading.Thread(target=select_MOJIA_agency, args=()).start()
    threading.Thread(target=move_action, args=()).start()
    threading.Thread(target=consumer_queue, args=()).start()
    threading.Thread(target=detect_enemy, args=()).start()
    threading.Thread(target=detect_battle, args=()).start()
    threading.Thread(target=attack_enemy, args=()).start()


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
