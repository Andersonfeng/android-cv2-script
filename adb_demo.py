import os
from time import sleep


def tap(x, y):
    os.system("adb shell input tap {} {}".format(x, y))


def swipe(x1, y1, x2, y2, time):
    os.system("adb shell input swipe {} {} {} {} {}".format(
        x1, y1, x2, y2, time))

# swipe(300,900,900,800)


# tap(100, 200)
for i in range(1000):
    swipe(300, 800, 500, 500, 5000)
    # tap(1735,900)
    sleep(0.5)
