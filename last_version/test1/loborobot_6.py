import RPi.GPIO as GPIO # type: ignore
import smbus # type: ignore
import time
import math
import pygame
import base64
import json
import requests
import cv2
import threading
from socket import  *

requests.DEFAULT_RETRIES = 5
s = requests.session()
# # 关闭多余连接
s.keep_alive = False

sock=socket(AF_INET,SOCK_DGRAM)
sock.bind(('192.168.137.106',8300))
# 创建PCA9685对象输出PWM信号
class PCA9685:
    # 初始化寄存器地址
    __SUBADR1__ = 0x02
    __SUBADR2__ = 0x03
    __SUBADR3__ = 0x04
    __MODE1__ = 0x00
    __PRESCALE__ = 0xFE
    __LED0_ON_L__ = 0x06
    __LED0_ON_H__ = 0x07
    __LED0_OFF_L__ = 0x08
    __LED0_OFF_H__ = 0x09
    __ALLLED_ON_L__ = 0xFA
    __ALLLED_ON_H__ = 0xFB
    __ALLLED_OFF_L__ = 0xFC
    __ALLLED_OFF_H__ = 0xFD

# class Loborobot:
    def __init__(self, address=0x40, debug=False):
        """
        :param address: I2C address of PCA9685
        :param debug: Print debug messages
        """
        # 创建I2C总线
        self.bus = smbus.SMBus(1) # 通常使用1来表示总线编号
        # 实例设备地址
        self.address = address
        # 实例调试模式
        self.debug = debug
        # 设置调试输出
        if self.debug:
            print("Reseting PCA9685")
        # 重置PCA9685
        self.write(self.__MODE1__, 0x00)

    # write方法，用于向PCA9685写入数据
    def write(self, reg, value):
        """
        :param reg: 寄存器地址
        :param value: 写入的8位值
        """
        # 通过I2C实例的写值方法，给对应的9685芯片对应寄存器总线写值
        self.bus.write_byte_data(self.address, reg, value)
        if self.debug:
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
    
    # read方法，用于从PCA9685读取数据
    def read(self, reg):
        """
        :param reg: 寄存器地址
        """
        # 通过I2C实例的读值方法，从对应的9685芯片对应寄存器总线读值
        value = self.bus.read_byte_data(self.address, reg)
        if self.debug:
            print("I2C: Read 0x%02X from register 0x%02X" % (value, reg))
        return value

    # setPWMFreq方法，用于设置PWM频率，写入预分频值
    def setPWMFreq(self, freq):
        """
        :param freq: PWM频率 一般50hz
        """
        # 设置频率变量
        prescaleval = 25000000.0 # 25MHz
        prescaleval /= 4096.0 # 设置最大频率为2^12 = 4096
        prescaleval /= float(freq) # 除去设定的参数频率
        prescaleval -= 1.0 # 减去1，确保预分频数是整数
        if self.debug:
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)        
        # 更改模式 写入预分频值
        # 计算预分频值
        prescale = int(math.floor(prescaleval) + 0.5) # 对预分频数进行取整 math.floor 或者使用int
        if self.debug:
            print("Final pre-scale: %d" % prescale)
        # 读取MODE1寄存器
        oldmode = self.read(self.__MODE1__) # 读取当前模式的值
        # 计算新的MODE1寄存器值
        newmode = (oldmode & 0x7F) | 0x10 # 创造一个新的模式值 把旧的模型值最低7位清零，第五位设置1
        # 为了让控制器进入休眠模式
        # 写入MODE1寄存器
        self.write(self.__MODE1__, newmode) # 把新模式值写入self.__model1让设备进入休眠模式         
        # 写入预分频值
        self.write(self.__PRESCALE__, prescale) # 将预分频值写入预分频值寄存器__prescale
        # 休眠2ms
        time.sleep(0.005)
        # 写入MODE1寄存器
        self.write(self.__MODE1__, oldmode)
        # 写入MODE1寄存器
        self.write(self.__MODE1__, oldmode | 0x80)
        if self.debug:
            print("Mode now: 0x%02X" % self.read(self.__MODE1__))
        
    # 定义一个setpwm方法，用于设置pwm通道的开关时间
    def setPWM(self, channel, on, off):
        """
        :param channel: pwm通道编号
        :param on:      脉宽调制开始时间
        :param off；    脉宽调制结束时间
        """
        # 写入开始时间
        self.write(self.__LED0_ON_L__ + 4 * channel, on&0xFF)
        self.write(self.__LED0_ON_H__ + 4 * channel, on>>8)
        # 写入结束时间
        self.write(self.__LED0_OFF_L__ + 4 * channel, off&0xFF)
        self.write(self.__LED0_OFF_H__ + 4 * channel, off>>8)
        if self.debug:
            print('channel', 'on', 'off', channel, on, off)
    
    def setdutycycle(self, channel, P):
        """
        :param channel: pwm通道编号
        :param p:       占空比的百分比 0———100之间 
        """
        # 计算pwm结束时间
        # 9685分辨率12bit 2^12 = 4096
        # 计数 = 4096 / 100
        # 注意 最大值为4095 按上述计算方式占空比不能为100
        self.setPWM(channel, 0, int(P * (4096 / 100)))

    # 定义一个setlevel方法，用于设置pwm通道的输出电平
    def setlevel(self, channel, value):
        """
        :param channel: pwm通道编号
        :param value:   0或1
        """
        if value == 1:
            self.setPWM(channel, 0, 4095)
        else:
            self.setPWM(channel, 0, 0)

# 小车电机旋转测试
class LOBOROBOT:
    def __init__(self):
        #引脚编号设置
        # 左前电机
        self.PWMA = 0
        self.AIN1 = 2
        self.AIN2 = 1
        # 右前电机
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4
        # 左后电机
        self.PWMC = 6
        self.CIN1 = 8
        self.CIN2 = 7
        # 右后电机
        self.PWMD = 11
        self.DIN1 = 25
        self.DIN2 = 24
        #传感器
        self.sensorleft = 12
        self.sensorright = 16
        #按钮
        self.btpin=19
        self.gpin = 5
        self.Rpin = 6
        #舵机
        self.PWM9=16
        self.PWM10=17


        #GPIO设置模式
        # 初始化9685
        self.pwm = PCA9685(0x40, debug=False)
        # 设置初始频率
        self.pwm.setPWMFreq(50)
        GPIO.setwarnings(False)
        # 设置GPIO的编码
        GPIO.setmode(GPIO.BCM)
        # 设置GPIO模式
        GPIO.setup(self.DIN1, GPIO.OUT)
        GPIO.setup(self.DIN2, GPIO.OUT)

        GPIO.setup(self.sensorleft, GPIO.IN)  # GPIO接口设置输入模式
        GPIO.setup(self.sensorright, GPIO.IN)

        # 设置对应按钮和灯连接引脚的模式  输入输出
        GPIO.setup(self.gpin, GPIO.OUT)
        GPIO.setup(self.Rpin, GPIO.OUT)
        # 按键输入模式
        GPIO.setup(self.btpin, GPIO.IN)


        #车辆控制模式
        self.line_search_mode=0
        self.obStacle_avoid_mode=0


    #车轮控制函数
    def wheelrun(self,num,speed,index=1):
        if speed > 100 or speed<0:
            return
        if index==0:
            return
        if index<0:
            index=-1
        if index>0:
            index=1

        if num==0:
            self.pwm.setdutycycle(self.PWMA, speed)
            if index==1:
                self.pwm.setlevel(self.AIN1, 0)
                self.pwm.setlevel(self.AIN2, 1)
            if index == -1:
                self.pwm.setlevel(self.AIN1, 1)
                self.pwm.setlevel(self.AIN2, 0)
        if num==1:
            self.pwm.setdutycycle(self.PWMB, speed)
            if index==1:
                self.pwm.setlevel(self.BIN1, 1)
                self.pwm.setlevel(self.BIN2, 0)
            if index == -1:
                self.pwm.setlevel(self.BIN1, 0)
                self.pwm.setlevel(self.BIN2, 1)
        if num==2:
            self.pwm.setdutycycle(self.PWMC, speed)
            if index==1:
                self.pwm.setlevel(self.CIN1, 1)
                self.pwm.setlevel(self.CIN2, 0)
            if index == -1:
                self.pwm.setlevel(self.CIN1, 0)
                self.pwm.setlevel(self.CIN2, 1)
        if num==3:
            self.pwm.setdutycycle(self.PWMD, speed)
            if index==1:
                GPIO.output(self.DIN1, 0)
                GPIO.output(self.DIN2, 1)
            if index == -1:
                GPIO.output(self.DIN1, 1)
                GPIO.output(self.DIN2, 0)

    # 车轮控制函数
    def wheelstop(self, num):
        if num==0:
            self.pwm.setdutycycle(self.PWMA, 0)
            self.pwm.setlevel(self.AIN1, 0)
            self.pwm.setlevel(self.AIN2, 0)

        if num==1:
            self.pwm.setdutycycle(self.PWMB, 0)
            self.pwm.setlevel(self.BIN1, 0)
            self.pwm.setlevel(self.BIN2, 0)
        if num==2:
            self.pwm.setdutycycle(self.PWMC, 0)
            self.pwm.setlevel(self.CIN1, 0)
            self.pwm.setlevel(self.CIN2, 0)
        if num==3:
            self.pwm.setdutycycle(self.PWMD, 0)
            GPIO.output(self.DIN1, 0)
            GPIO.output(self.DIN2, 0)

    #全车轮停止
    def stop(self):
        for i in range(0,4):
            self.wheelstop(i)


    # 前进
    def forward(self, speed,t_time):
        dir=[1,1,1,1]
        for i in range(0,4):
            self.wheelrun(i,speed,dir[i])
        time.sleep(t_time)
        self.stop()

    # 转前进
    def forward_t(self, speed):
        dir = [1, 1, 1, 1]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])

    # 后退
    def back(self, speed,t_time):
        dir = [-1, -1, -1, -1]
        for i in range(0, 4):
            self.wheelrun(i,speed,dir[i])
        time.sleep(t_time)
        self.stop()
    # 转后退
    def back_t(self, speed):
        dir = [-1, -1, -1, -1]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
    # 左移
    def movleft(self, speed,t_time):
        dir = [-1, 1, 1, -1]
        for i in range(0, 4):
            self.wheelrun(i,speed,dir[i])
        time.sleep(t_time)
        self.stop()
    # 转左移
    def movleft_t(self, speed):
        dir = [-1, 1, 1, -1]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
    # 右移
    def movright(self, speed,t_time):
        dir = [1, -1, -1, 1]
        for i in range(0, 4):
            self.wheelrun(i,speed,dir[i])
        time.sleep(t_time)
        self.stop()
    # 转右移
    def movright_t(self, speed):
        dir = [1, -1, -1, 1]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
    # 左转
    def turnleft(self, speed,t_time):
        dir = [-1, 1, -1, 1]
        for i in range(0, 4):
            self.wheelrun(i,speed,dir[i])
        time.sleep(t_time)
        self.stop()
    # 转左转
    def turnleft_t(self, speed):
        dir = [-1, 1, -1, 1]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
    # 右转
    def turnright(self, speed,t_time):
        dir = [1, -1, 1, -1]
        for i in range(0, 4):
            self.wheelrun(i,speed,dir[i])
        time.sleep(t_time)
        self.stop()
    # 转右转
    def turnright_t(self, speed):
        dir = [1, 1, 1, 1]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
    
    # 前左斜
    def forward_left(self, speed,t_time):
        dir = [0, 1, 1, 0]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
        time.sleep(t_time)
        self.stop()
    
    # 前右斜
    def forward_right(self, speed,t_time):
        dir = [1, 0, 0, 1]
        for i in range(0, 4):
            self.wheelrun(i,speed,dir[i])
        time.sleep(t_time)
        self.stop()
    
    # 左后斜
    def back_left(self, speed,t_time):
        dir = [-1, 0, 0, -1]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
        time.sleep(t_time)
        self.stop()

    # 右后斜
    def back_right(self, speed,t_time):
        dir = [0, -1, -1, 0]
        for i in range(0, 4):
            self.wheelrun(i, speed, dir[i])
        time.sleep(t_time)
        self.stop()
    # 播放指定的音乐
    def music_play(self,file):
        file_text=file+".mp3"
        pygame.mixer.init()
        pygame.mixer.music.load(file_text)
        pygame.mixer.music.play()
        time.sleep(1)
    #红外传感器检测障碍物 返回障碍物位置
    def sense(self):

        sl = GPIO.input(self.sensorleft)
        sr = GPIO.input(self.sensorright)
        if sl == True and sr == True:
            return 5
            # print('无障碍，继续行进')
        if sl == True and sr == False:
            return 6
            # print(('右侧有障碍，往左偏移'))
        if sl == False and sr == True:
            return 4
            # print('左侧有障碍，往右偏移')
        if sl == False and sr == False:
            return 8
            # print('前方有障碍，向后退，选择向左或向右')
    def btncheck(self):
        # 检测按键
        if GPIO.input(self.btpin) == True:
            time.sleep(0.1)
            if GPIO.input(self.btpin) == True:
                GPIO.output(self.gpin, 0)
                GPIO.output(self.Rpin, 1)
                return 0
        elif GPIO.input(self.btpin) == False:
            time.sleep(0.1)
            if GPIO.input(self.btpin) == False:
                GPIO.output(self.gpin, 1)
                GPIO.output(self.Rpin, 0)
                return 1
        return 2

    # 辅助功能，使设置舵机脉冲宽度更简单。
    def set_servo_pulse(self, channel, pulse):
        pulse_length = 1000000  # 1,000,000 us per second
        pulse_length //= 60  # 60 Hz
        print('{0}us per period'.format(pulse_length))
        pulse_length //= 4096  # 12 bits of resolution
        print('{0}us per bit'.format(pulse_length))
        pulse *= 1000
        pulse //= pulse_length
        self.pwm.setPWM(channel, 0, pulse)
    #设置一个方法 传入角度0-180 来控制舵机
    #20ms脉冲宽带 0°  0.5  180°  2.5
    def set_servo_angle(self,channel,angle):
        angle=4096*((angle*11)+500)/20000
        self.pwm.setPWM(channel,0,int(angle))
    #循线
    def line_along(self,lspeed,aspeed,lper,aper,camera):
        i=0
        linespeed=lspeed
        anglespeed=aspeed
        lineper=lper
        angleper=aper
        came=camera
        self.set_servo_angle(10, 90)
        self.set_servo_angle(9, 150)
        #连续直行次数 转弯次数计数 偏角计数
        linecount = 0
        rowcount = 0
        anglecount = 0
        #i控制运行时间
        while i<100 and self.sense()==5 and self.image_dispose(came)==0:
            #根据摄像头返回的中心点位置执行对应操作 通过小键盘方向代替上8下2左4右6
            #camera_result即检测到的黑线位置，小键盘标识
            if came.camera_result == 8:
                #直行时清空转弯计数 增加直行计数
                rowcount = 0
                anglecount =0
                self.forward(linespeed, lineper)
                linecount += 1
                i = i + lineper
            if came.camera_result == 4:
                #线位于左侧
                #转弯时清空直行计数，同时增加转弯计数，转弯速度会不断加快
                #anglecount记录累计偏角，用于识别摆动
                linecount = 0
                rowcount += 1
                anglecount -=1
                self.turnleft(min(anglespeed*(1+rowcount*0.1),50), angleper)
                i = i + angleper
                #如果检测到转弯次数过多
                if rowcount > 15 and abs(anglecount)<3:
                    #转弯多偏角小，为摆动 适当前移 清空转弯计数重置转弯幅度
                    self.forward(linespeed*0.5,lineper)
                    rowcount=0
                    anglecount=0
                if rowcount >20:
                    #转弯过多自动停止
                    i+=100
                    self.stop()

            if came.camera_result == 6:
                #线位于右侧同上
                linecount = 0
                rowcount += 1
                anglecount -= 1
                self.turnright(min(anglespeed * (1 + rowcount * 0.1), 50), angleper)
                i = i + angleper
                # 如果检测到
                if rowcount > 15 and abs(anglecount) < 3:
                    self.forward(linespeed * 0.5, lineper)
                    rowcount = 0
                    anglecount = 0
                if rowcount > 20:
                    i += 100
                    self.stop()

            if came.camera_result == 5:
                #找不到线
                self.line_find(linespeed,anglespeed,lineper,angleper,came)

        self.stop()

    #找线 用于在摄像头找不到线时不断左右转动，直到找到线为止
    def line_find(self,lspeed,aspeed,lper,aper,camera):
        self.set_servo_angle(9, 130)
        linespeed=lspeed
        anglespeed=aspeed
        lineper=lper
        angleper=aper
        came=camera
        #运行时找不到线 启用找线模块 为防止直接掉头 采用左右交替转动的模式
        self.set_servo_angle(9, 150)
        i = 1
        while came.camera_result == 5 and i < 15:
            if i > 0:
                self.turnright(anglespeed * 2, 2*angleper * abs(i))
                i =i+1
            if i < 0:
                self.turnleft(anglespeed * 2, 2*angleper * abs(i))
                i =i-1
            i = -i
        if came.camera_result == 5:
            self.turnleft(anglespeed * 2, 2*angleper * (2*i-1))
            self.forward(linespeed, lineper)
        self.set_servo_angle(9, 150)
    #避障
    def obstacle_avoid(self,camera):
        speed=50
        came=camera
        while self.sense()!=5 or came.camera_result==5:
            if self.sense()!=5:
                while self.sense()!=5:
                    if self.sense()==6:
                        self.movleft_t(speed)
                    if self.sense()==4:
                        self.movright_t(speed)
                time.sleep(0.5)
                self.stop()
            if self.sense()==5 and came.camera_result==5:
                while self.sense()==5 and came.camera_result==5:
                    self.forward_t(speed)
                self.stop()

    def image_dispose(self,camera):
        came=camera
        if came.light_result==0 and came.qr_result=='None' and came.sign_result=='':
            return 0
        if came.light_result!=0:
            if came.light_result == 1:
                print('识别红灯')
                self.music_play('识别红灯')
                l.stop()
                while came.light_result != 3:
                    l.stop()
                print('识别绿灯')
                self.music_play('识别绿灯')
        # if came.qr_result != 0:
        #     self.music_play('识别二维码')
        if came.sign_result != '':
            self.music_play(came.sign_result)
        return 1




#        障碍          有        无
#线
#有               避障         循线
#无              避障         找线





class camera_thread(threading.Thread):
    def __init__(self, n):
        super().__init__() #必须调用父类的初始化方法
        self.camera_result = n
        self.light_result=0
        self.qr_result = ''
        self.sign_result=''

    def run(self) -> None:
        cap = cv2.VideoCapture(0)
        cap.set(3, 1080)
        cap.set(4, 720)
        i = 0  # 初始值
        j = 60  # 帧数
        while True:
            # 1.从摄像头中读取每一帧图片
            ret, frame = cap.read()
            if ret:
                #从摄像头画面中找线的位置，返回到camera_result中
                # 对读取到的fram进行裁剪 只保留一半
                crop_img = frame[0:720, 0:1080]
                # 将裁剪后的图片 转为灰度图像
                grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
                # 对转换的灰度图 进行高斯模糊处理
                blur = cv2.GaussianBlur(grey, (5, 5), 0)
                # 图像的二值化
                ret, thresh1 = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
                # 腐蚀
                mask = cv2.erode(thresh1, None, iterations=2)
                # 膨胀
                mask = cv2.dilate(mask, None, iterations=2)
                # 获取当前帧的所有轮廓
                image,contours, heir = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
                # 检查轮廓列表是否有轮廓
                if len(contours) > 0:
                    # 使用max ()求最大轮廓
                    c = max(contours, key=cv2.contourArea)
                    # 拿到轮廓的矩
                    M = cv2.moments(c)
                    # 计算中心点坐标x,y,M['m10]与面积相除 得到x轴质心
                    x = int(M['m10'] / M['m00'])
                    y = int(M['m01'] / M['m00'])
                    # 绘制竖线
                    cv2.line(crop_img, (x, 0), (x, 720), (255, 0, 0), 1)
                    # 绘制横线
                    cv2.line(crop_img, (0, y), (1200, y), (255, 0, 0), 1)
                    if x > 840:
                        self.camera_result = 6
                    if x < 840 and x > 240:
                        self.camera_result = 8
                    if x < 240:

                        self.camera_result = 4
                else:
                    self.camera_result= 5
                cv2.imshow('frame', mask)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print('stop')
                    self.camera_result=0
            else:
                print('摄像头读取画面失败')
            if i % j == 0:
                #     ret, frame = cap.read()
                # 将每一帧转为ipg格
                #
                # 式字节流
                ret, jpg = cv2.imencode('.jpg', frame)
                jpg_bytes = jpg.tobytes()
                # 为保证数据的完整性和安全性 base64编码方式
                base64_data = base64.b64encode(jpg_bytes).decode()
                data = {'img': base64_data}
                # r = requests.post('http://127.0.0.1:8000/test', data=json.dumps(data))
                r = requests.post('http://192.168.173.170:8000/test', data=json.dumps(data))
                print(r.status_code)
                print(r.json())
                self.light_result=r.json()["light"]
                print(self.light_result)
                self.qr_result=r.json()["qr"]
                print(self.qr_result)
                self.sign_result=r.json()["sign"]
                print(self.sign_result)

            i += 1




if __name__ == '__main__':



    i=0
    per=0.2
    lineper=0.2
    angleper=0.1
    speed=50
    linespeed=35
    anglespeed=20
    l = LOBOROBOT()
    l.set_servo_angle(10, 90)
    l.set_servo_angle(9, 120)

    #多进程 摄像头输出
    came = camera_thread(0)
    came.start()



    #按钮控制
    '''
    print(l.btncheck())
    try:
        while True:
    except KeyboardInterrupt:
            l.stop()
    '''


    #网络控制
    try:
        while True:
            data, address = sock.recvfrom(1024)
            #d 指令获取
            d = data.decode()
            sock.sendto('执行成功'.encode(), address)
            print(d)
            # if d =='l':
            #     l.line_serch(50,0.2,0.1,came)
            #s 启动
            if d=='s':
                while True:
                    #优先避障
                    l.obstacle_avoid(came)

                    #摄像头识别
                    while l.image_dispose(came)!=0:
                        l.stop()

                    #无障碍物后执行循线 内部存在中断条件
                    l.line_along(linespeed,anglespeed,lineper,angleper,came)








    except KeyboardInterrupt:
        l.stop()

