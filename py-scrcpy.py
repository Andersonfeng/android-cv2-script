'''
https://github.com/Allong12/py-scrcpy/blob/master/scrcpy_client.py

# upload jar
adb push "D:\Program Files\scrcpy-win64-v1.24\scrcpy-server" /data/local/tmp/

# run jar
adb shell CLASSPATH=/data/local/tmp/scrcpy-server app_process / com.genymobile.scrcpy.Server 1.24 'log_level=INFO' 'bit_rate=10000' 'max_size=0' 'max_fps=0' 'lock_video_orientation=-1' 'tunnel_forward=true' 'control=true' 'display_id=0' 'show_touches=false' 'stay_awake=true' 'encoder_name= ' 'power_off_on_close=false' 'clipboard_autosync=false' 

# forward prot
adb forward tcp:8080 localabstract:scrcpy


# control event ref: https://www.codenong.com/j5e743bb4f265da57520/
1位: 控制类型 type
1位: action 表示按下/抬起/滑动 事件
8位: pointerId 不知用处
12位: Position 其中8位分别每4位表示点击的x,y 坐标 另外4位分别表示屏幕宽高
2位:presureInt 按压力度
4位: buttons 不知用处

按下
[
2,
0,
0,0,0,0,0,0,0,0,
x >> 24,x << 8 >> 24,x << 16 >> 24,x << 24 >> 24,
y >> 24,y << 8 >> 24,y << 16 >> 24,y << 24 >> 24,
1080 >> 8,1080 << 8 >> 8,2280 >> 8,2280 << 8 >> 8,
0,
0,
0,
0,
0,
0
]
'''

import socket
import struct
import sys
import os
import subprocess
import io
import time
import numpy as np
import logging

from threading import Thread
from queue import Queue, Empty

SVR_maxSize = 600
SVR_bitRate = 999999999
SVR_tunnelForward = "true"
SVR_crop = "9999:9999:0:0"
SVR_sendFrameMeta = "true"

IP = '127.0.0.1'
PORT = 8080
RECVSIZE = 0x10000
HEADER_SIZE  = 12

SCRCPY_dir = 'D:\\Program Files\\scrcpy-win64-v1.24'
FFMPEG_bin = 'ffmpeg'
device_ip = '192.168.50.119:5555'
ADB_bin = os.path.join(SCRCPY_dir,"adb")

#fd = open("savesocksession",'wb')

logger = logging.getLogger(__name__)

class SCRCPY_client():
    def __init__(self):
        self.bytes_sent = 0
        self.bytes_rcvd = 0
        self.images_rcvd = 0
        self.bytes_to_read = 0
        self.FFmpeg_info = []
        self.ACTIVE = True
        self.LANDSCAPE = True
        self.FFMPEGREADY = False
        self.ffoutqueue = Queue()


    def stdout_thread(self):
        logger.info("START STDOUT THREAD")
        while self.ACTIVE:
            rd = self.ffm.stdout.read(self.bytes_to_read)
            if rd:
                self.bytes_rcvd += len(rd)
                self.images_rcvd += 1
                self.ffoutqueue.put(rd)
        logger.info("FINISH STDOUT THREAD")

    def stderr_thread(self):
        logger.info("START STDERR THREAD")
        while self.ACTIVE:
            rd = self.ffm.stderr.readline()
            if rd:
                self.FFmpeg_info.append(rd.decode("utf-8"))
        logger.info("FINISH STDERR THREAD")

    def stdin_thread(self):
        logger.info("START STDIN THREAD")
        
        while self.ACTIVE:
            # if SVR_sendFrameMeta:
            header = self.video_socket.recv(HEADER_SIZE)
            
            pts = int.from_bytes(header[:8],
                byteorder='big', signed=False)
            frm_len = int.from_bytes(header[8:],
                byteorder='big', signed=False)      
        
            data = self.video_socket.recv(frm_len)
            
            logger.info('=====Write stdin start')

            self.bytes_sent += len(data)
            self.ffm.stdin.write(data) #这里阻塞了 why
            logger.info("=====Write stdin done")
            self.ffm.stdin.flush()
            # else:
            # data = self.video_socket.recv(RECVSIZE)
            # self.bytes_sent += len(data)
            # self.ffm.stdin.write(data)

        logger.info("FINISH STDIN THREAD")

    def get_next_frame(self, most_recent=False):
        if self.ffoutqueue.empty():
            return None
        # logger.info('queue size:%s',self.ffoutqueue.qsize())
        if most_recent:
            frames_skipped = -1
            while not self.ffoutqueue.empty():
                frm = self.ffoutqueue.get()
                frames_skipped +=1
        else:
            frm = self.ffoutqueue.get()

        frm = np.frombuffer(frm, dtype=np.ubyte)
        frm = frm.reshape((self.HEIGHT, self.WIDTH, 3))
        return frm
        # PIL.Image.fromarray(np.uint8(rgb_img*255))

    def connect(self):
        logger.info("Connecting")
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket.connect((IP, PORT))

        DUMMYBYTE = self.video_socket.recv(1)
        #fd.write(DUMMYBYTE)
        if not len(DUMMYBYTE):
            logger.error("Did not recieve Dummy Byte!")
            raise ConnectionError("Did not recieve Dummy Byte!")
        else:
            logger.info("Connected!")
            logger.info(DUMMYBYTE)


        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.connect((IP, PORT))

        self.video_socket.send('hello'.encode("utf-8"))
        # Receive device specs
        devname = self.video_socket.recv(64)
        
        #fd.write(devname)
        self.deviceName = devname.decode("utf-8")
        
        if not len(self.deviceName):
            raise ConnectionError("Did not recieve Device Name!")
        logger.info("Device Name: "+self.deviceName)
        
        res = self.video_socket.recv(4)
        #fd.write(res)
        self.WIDTH, self.HEIGHT = struct.unpack(">HH", res)
        logger.info("WxH: "+str(self.WIDTH)+"x"+str(self.HEIGHT))

        self.bytes_to_read = self.WIDTH * self.HEIGHT * 3
        
        return True
        
    def start_processing(self, connect_attempts=200):
        # Set up FFmpeg 
        ffmpegCmd = [FFMPEG_bin, '-y', #-y 直接覆盖输出文件
                     '-r', '60',  # -r 设置帧率
                     '-i', 'pipe:0', # -i 采集的数据源
                     '-vcodec', 'rawvideo', # -vcodec 视频编解码器 -codec:v 的别名
                     '-pix_fmt', 'rgb24',  # -pix_fmt 像素格式
                     '-f', 'image2pipe', # -f 强制输入输出文件格式
                     'pipe:1'] 
        try:
            self.ffm = subprocess.Popen(ffmpegCmd,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Couldn't find FFmpeg at path FFMPEG_bin: "+
                            str(FFMPEG_bin))
        self.ffoutthrd = Thread(target=self.stdout_thread,
                                args=())
        self.fferrthrd = Thread(target=self.stderr_thread,
                                args=())
        self.ffinthrd = Thread(target=self.stdin_thread,
                               args=())
        self.ffoutthrd.daemon = True
        self.fferrthrd.daemon = True
        self.ffinthrd.daemon = True

        self.fferrthrd.start()
        time.sleep(0.25)
        self.ffinthrd.start()
        time.sleep(0.25)
        self.ffoutthrd.start()

        logger.info("Waiting on FFmpeg to detect source")
        for i in range(connect_attempts):
            if any(["Output #0, image2pipe" in x for x in self.FFmpeg_info]):
                logger.info("Ready!")
                self.FFMPEGREADY = True
                break
            time.sleep(1)
            logger.info('still waiting on FFmpeg...')
        else:
            logger.error("FFmpeg error?")
            logger.error(''.join(self.FFmpeg_info))
            raise Exception("FFmpeg could not open stream")
        return True
    
    def kill_ffmpeg(self):
        self.ffm.terminate()
        self.ffm.kill()  
        #self.ffm.communicate()
    def __del__(self):
        
        self.ACTIVE = False
        
        self.fferrthrd.join()
        self.ffinthrd.join()
        self.ffoutthrd.join()
        
def connect_and_forward_scrcpy():
    try:
        logger.info("Upload JAR...")
        adb_push = subprocess.Popen(
            [ADB_bin,'-s'+device_ip,'push',
            os.path.join(SCRCPY_dir,'scrcpy-server'),
            '/data/local/tmp/'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=SCRCPY_dir)

        # adb_push_comm = ''.join([x.decode("utf-8") for x in adb_push.communicate() if x is not None])
        adb_push.wait()
        logger.info('out:%s',adb_push.stdout.read())
        logger.info('err:%s',adb_push.stderr.read())
        
        # if "error" in adb_push_comm:
            # logger.critical("Is your device/emulator visible to ADB?")
            # raise Exception(adb_push_comm)
        '''
        ADB Shell is Blocking, don't wait up for it 
        Args for the server are as follows:
        maxSize         (integer, multiple of 8) 0
        bitRate         (integer)
        tunnelForward   (optional, bool) use "adb forward" instead of "adb tunnel"
        crop            (optional, string) "width:height:x:y"
        sendFrameMeta   (optional, bool) 
        
        '''
        logger.info("Run JAR")

        subprocess.Popen(
            [ADB_bin,'-s'+device_ip,'shell',
            'CLASSPATH=/data/local/tmp/scrcpy-server',
            'app_process',
            '/',
            'com.genymobile.scrcpy.Server',
            '1.24',
            'log_level=INFO',
            'bit_rate=800000',
            'max_size=0',
            'max_fps=60',
            'lock_video_orientation=-1',
            'tunnel_forward=true',
            'control=true',
            'display_id=0',
            'show_touches=false',
            'stay_awake=true',
            # 'power_off_on_close=false',
            # 'encoder_name= ',
            # 'clipboard_autosync=false',
            # 'send_frame_meta=true',
            # 'crop= ',
            # 'codec_options=-',
            # 'downsize_on_error=false',
            # 'cleanup=false',
            # 'power_on=false'
            ],
            cwd=SCRCPY_dir)

        time.sleep(1)

        subprocess.Popen(
            [ADB_bin,'-s'+device_ip,'forward',
            'tcp:8080','localabstract:scrcpy'],
            cwd=SCRCPY_dir).wait()
        time.sleep(1)

        logger.info("Forward Port complete")

    except FileNotFoundError:
        raise FileNotFoundError("Couldn't find ADB at path ADB_bin: "+
                    str(ADB_bin))
    return True

def show_image():
    import cv2
    try:
        count = 1
        while True:
            frm = SCRCPY.get_next_frame(most_recent=False)
            if isinstance(frm, (np.ndarray, np.generic)):
                frm = cv2.cvtColor(frm, cv2.COLOR_RGB2BGR)                
                count += 1
                count = count % 5
                # cv2.imwrite('D:\\Projects\\Python\\android-simulator-script\\simulator\\screenshot\\screenshot_'+str(count)+'.png',frm)
                cv2.imshow("screen", frm)
                cv2.waitKey(1000//60)  # CAP 60FPS
                
    except KeyboardInterrupt:
        from IPython import embed
        embed()
    finally:
        pass

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    assert connect_and_forward_scrcpy()
        
    SCRCPY = SCRCPY_client()
    SCRCPY.connect()
    SCRCPY.start_processing()
    
    Thread(target=show_image, args=()).start()

    # import cv2
    # try:
    #     count = 0
    #     while True:
    #         frm = SCRCPY.get_next_frame(most_recent=False)
    #         if isinstance(frm, (np.ndarray, np.generic)):
    #             frm = cv2.cvtColor(frm, cv2.COLOR_RGB2BGR)
    #             # cv2.VideoCapture(frm)
    #             # count += 1
    #             # cv2.imwrite('D:\\Projects\\Python\\android-simulator-script\\simulator\\screenshot\\screenshot_'+str(count)+'.png',frm)
    #             cv2.imshow("screen", frm)
    #             cv2.waitKey(1000//60)  # CAP 60FPS
                
    # except KeyboardInterrupt:
    #     from IPython import embed
    #     embed()
    # finally:
    #     pass
        #fd.close()