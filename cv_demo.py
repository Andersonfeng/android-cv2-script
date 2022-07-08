from time import sleep
import os
import cv2
import numpy
import threading
import sys

threshold = 0.8


def match_screenshot(target_path, template_path):
    target = cv2.imread(target_path)
    template = cv2.imread(template_path)
    theight, twidth = template.shape[:2]
    print(theight, twidth)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(sys._getframe().f_code.co_name, template_path, max_val, max_loc)
    cv2.line(target,(0,0),(100,1000),             (0, 255, 0),             1)
    cv2.imshow('result', target)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


match_screenshot('./simulator/screenshot/screenshot-copy.png',
                 './simulator/battle.png')
