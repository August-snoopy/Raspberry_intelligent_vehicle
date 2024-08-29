# 通过红外传感器来检测前方障碍物
# 通过连接的接口来检测红外传感器
# 判断输出的内容
import RPi.GPIO as GPIO # type: ignore
import smbus # type: ignore
import time
import math
import pygame
# 用于多任务处理
import threading
from multiprocessing import Process, Queue
from pynput import keyboard # type: ignore
# 用于创建UDP套接字
from socket import *
# 使用opencv检测黑线循迹
import cv2



dir = ['f', 'b']
pook = 8000


# 用于PCA9685的PWM控制对电路进行控制
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

# 小车电机运动控制
class LOBOROBOT:
    def __init__(self):
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

    # 封装一个小车轮子旋转的函数
    def mrun(self, m, index, speed):
        """
        :param m:     电机编号
        :param index: 电机方向 f标志正转，b标志反转
        :param speed: 电机速度
        """
        if speed > 100 or speed < 0:
            return
        if m == 0:
            self.pwm.setdutycycle(self.PWMA, speed)
            if index == dir[0]:
                self.pwm.setlevel(self.AIN1, 0)
                self.pwm.setlevel(self.AIN2, 1)
            else:
                self.pwm.setlevel(self.AIN1, 1)
                self.pwm.setlevel(self.AIN2, 0) 
        elif m == 1:
            self.pwm.setdutycycle(self.PWMB, speed)
            if index == dir[0]:
                self.pwm.setlevel(self.BIN1, 1)
                self.pwm.setlevel(self.BIN2, 0)
            else:
                self.pwm.setlevel(self.BIN1, 0)
                self.pwm.setlevel(self.BIN2, 1)
        elif m == 2:
            self.pwm.setdutycycle(self.PWMC, speed)
            if index == dir[0]:
                self.pwm.setlevel(self.CIN1, 1)
                self.pwm.setlevel(self.CIN2, 0)
            else:
                self.pwm.setlevel(self.CIN1, 0)
                self.pwm.setlevel(self.CIN2, 1)
        elif m == 3:
            self.pwm.setdutycycle(self.PWMD, speed)
            if index == dir[0]:
                GPIO.output(self.DIN1, 0)
                GPIO.output(self.DIN2, 1)
            else:
                GPIO.output(self.DIN1, 1)
                GPIO.output(self.DIN2, 0)
        else:
            return
    
    # 对应电机停止函数
    def m_stop(self, m):
        """
        :param m: 电机编号
        """
        if m == 0:
            self.pwm.setdutycycle(self.PWMA, 0)
        elif m == 1:
            self.pwm.setdutycycle(self.PWMB, 0)
        elif m == 2:
            self.pwm.setdutycycle(self.PWMC, 0)
        elif m == 3:
            self.pwm.setdutycycle(self.PWMD, 0)
        else:
            return

    # 前进
    def turn_up(self, speed, t):
        """
        :param speed: 速度
        :param t:     运行时间
        """
        self.mrun(0, 'f', speed)
        self.mrun(1, 'f', speed)
        self.mrun(2, 'f', speed)
        self.mrun(3, 'f', speed)
        time.sleep(t)

    # 后退
    def turn_down(self, speed, t):
        """
        :param speed: 速度
        :param t:     运行时间
        """
        self.mrun(0, 'b', speed)
        self.mrun(1, 'b', speed)
        self.mrun(2, 'b', speed)
        self.mrun(3, 'b', speed)
        time.sleep(t)

    # 左移
    def moveleft(self, speed, t):
        """
        :param speed: 速度
        :param t:     运行时间
        """
        self.mrun(0, 'b', speed)
        self.mrun(1, 'f', speed)
        self.mrun(2, 'f', speed)
        self.mrun(3, 'b', speed)
        time.sleep(t)

    # 右移
    def moveright(self, speed, t):
        """
        :param speed: 速度
        :param t:     运行时间
        """
        self.mrun(0, 'f', speed)
        self.mrun(1, 'b', speed)
        self.mrun(2, 'b', speed)
        self.mrun(3, 'f', speed)
        time.sleep(t)
    # 左转
    def turn_left(self, speed, t):
        """
        :param speed: 速度
        :param t:     运行时间
        """
        self.mrun(0, 'b', speed)
        self.mrun(1, 'f', speed)
        self.mrun(2, 'b', speed)
        self.mrun(3, 'f', speed)
        time.sleep(t)

    # 右转
    def turn_right(self, speed, t):
        """
        :param speed: 速度
        :param t:     运行时间
        """
        self.mrun(0, 'f', speed)
        self.mrun(1, 'b', speed)
        self.mrun(2, 'f', speed)
        self.mrun(3, 'b', speed)
        time.sleep(t)
    
    # 停止
    def turnstop(self):
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
    
    # 左前
    def left_up(self, speed, t):
        self.m_stop(0)
        self.mrun(1, 'f', speed)
        self.mrun(2, 'f', speed)
        self.m_stop(3)
        time.sleep(t)
        
    # 右前
    def right_up(self, speed, t):
        self.mrun(0, 'f', speed)
        self.m_stop(1)
        self.m_stop(2)
        self.mrun(3, 'f', speed)
        time.sleep(t)

    # 左后
    def left_down(self, speed, t):
        self.m_stop(0)
        self.mrun(1, 'b', speed)
        self.mrun(2, 'b', speed)
        self.m_stop(3)
        time.sleep(t)

    # 右后
    def right_down(self, speed, t):
        self.mrun(0, 'b', speed)
        self.m_stop(1)
        self.m_stop(2)
        self.mrun(3, 'b', speed)
        time.sleep(t)
    
    def music_play(self,num):
        file_text=''
        if num == 'w':
            file_text='前进.mp3'
        if num == 's':
            file_text='后退.mp3'
        if num == 'a':
            file_text='左移.mp3'
        if num == 'd':
            file_text='右移.mp3'
        pygame.mixer.init()
        pygame.mixer.music.load(file_text)
        pygame.mixer.music.play()
        time.sleep(1)
        pygame.mixer.music.stop()

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
    
    # 辅助功能，使设置舵机脉冲宽度。
    def set_servo_pulse(self, channel, pulse):
        pulse_length = 1000000    # 1,000,000 us per second
        pulse_length //= 60       # 60 Hz
        print('{0}us per period'.format(pulse_length))
        pulse_length //= 4096     # 12 bits of resolution
        print('{0}us per bit'.format(pulse_length))
        pulse *= 1000
        pulse //= pulse_length
        self.pwm.setPWM(channel, 0, pulse)

    # 设置舵机角度函数  
    def set_servo_angle(self, channel, angle):
        angle=4096*((angle*11)+500)/20000
        self.pwm.setPWM(channel,0,int(angle))
    



# 避障线程
class ObstacleThread(threading.Thread):
    def __init__(self, loborobot, obstacleflag):
        threading.Thread.__init__(self)
        self.obstacleflag = obstacleflag
        self.running = True
        self.loborobot = loborobot
        # 初始化
        self.sensorleft = 12
        self.sensorright = 16
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sensorleft, GPIO.IN) # 左侧GPIO接口设置输入模式
        GPIO.setup(self.sensorright, GPIO.IN) #右侧GPIO接口设置输入模式  
    def run(self):
        while self.running:
            sl = GPIO.input(self.sensorleft) # 读取左侧传感器的值
            sr = GPIO.input(self.sensorright) # 读取右侧传感器的值
            # 判断左右两侧传感器的值是 高电平表示无障碍 
            if sl == True and sr == True:
                print("前方无障碍物，继续前进")
                self.loborobot.turn_up(50, 0.1)
                time.sleep(0.1)
            elif sl == True and sr == False:
                print("右侧有障碍物，往左偏移")
                self.loborobot.moveleft(50, 1)
                time.sleep(1)
            elif sl == False and sr == True:
                print("左侧有障碍物，往右偏移")
                self.loborobot.moveright(50, 1)
                time.sleep(1)
            elif sl == False and sr == False:
                print("前方有障碍物，向后退，选择向左或向右")
                self.loborobot.turn_down(50, 1)
                time.sleep(1)
                self.loborobot.turn_left(50, 1)
                time.sleep(1)
                self.loborobot.turn_up(50, 0.5)
                time.sleep(0.5)
                self.loborobot.turn_right(50, 1)
                time.sleep(1)
            self.loborobot.turnstop()
            self.loborobot.turn_up(50, 0.1)
            time.sleep(0.2)

    def stop(self):
        self.running = False
        GPIO.cleanup() # 清理GPIO资源

# PID控制器
class PIDController:
    """
    比例-积分-微分（PID）控制器的实现。
    参数:
        kp (float): 比例增益。
        ki (float): 积分增益。
        kd (float): 微分增益。
        setpoint (float): 控制器的期望设定点。
    """

    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.proportional = 0
        self.integral = 0
        self.differential = 0
        self.last_error = 0
        self.min = 0.9
        self.max = 120

    def update(self, measurement):
        """
        使用新的测量值更新控制器，并返回PID控制器计算的控制输出。
        参数:measurement (float): 当前的测量值。
        """
        error = self.setpoint - measurement
        self.proportional = error
        self.integral += error
        self.differential = error - self.last_error
        self.last_error = error
        output = self.kp * self.proportional + self.ki * self.integral + self.kd * self.differential
        output = max(min(output, self.max), self.min)
        return output
    
# 循迹线程
class TrackingThread(threading.Thread):
    def __init__(self, loborobot, trackingflag):
        threading.Thread.__init__(self)
        self.trackingflag = trackingflag
        self.running = True
        self.loborobot = loborobot
        self.cap = None
        self.speed = 50
        self.per = 0.1
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # 初始化PID控制器
        self.pid = PIDController(1.0, 0.1, 0.05, 0)

    def handle_turn(self, error, turn_angle, turn_func):
        if error > 0:
            if turn_angle > 10 and turn_angle < 20:
                print("好")
                turn_func(50, self.per)
                self.loborobot.turnstop()
                self.loborobot.turn_up(30, 0.3)
            elif turn_angle >= 20 and turn_angle < 40:
                print("还差一点")
                turn_func(50, self.per*5)
                self.loborobot.turnstop()
                self.loborobot.turn_up(30, 0.2)
            elif turn_angle >= 40 and turn_angle < 80:
                print("不太好")
                turn_func(50, self.per*10)
                self.loborobot.turnstop()
                self.loborobot.turn_up(30, 0.1)
            else:
                print("直行!")
                self.loborobot.turn_up(30, 0.5)
        if error < 0:    
            if turn_angle > 10 and turn_angle < 20:
                print("好")
                self.loborobot.turn_left(50, self.per)
                self.loborobot.turnstop()
                self.loborobot.turn_up(30, 0.3)
            if turn_angle >= 20 and turn_angle < 40:
                print("还差一点")
                self.loborobot.turn_left(50, self.per*5)
                self.loborobot.turnstop()
                self.loborobot.turn_up(30, 0.2)
            if turn_angle >= 40 and turn_angle < 80:
                print("不太好")
                self.loborobot.turn_left(50, self.per*10)
                self.loborobot.turnstop()
                self.loborobot.turn_up(30, 0.1)
            else:
                print("直行!")
                self.loborobot.turn_up(30, 0.5)
        else:
            print("直行!")
            self.loborobot.turn_up(30, 0.5)       

    def handle_no_path(self, is_rotating, start_time):
        if not is_rotating:
            start_time = time.time()
            is_rotating = True
        elif time.time() - start_time > 4:
            self.loborobot.turnstop()
            print("不能找到路径")
        print("寻路ing", time.time() - start_time)
        self.loborobot.turn_left(50, 0.05) 
        self.loborobot.turnstop()
        return is_rotating, start_time

    def process_image(self, frame):
        # 对读取到的frame进行裁剪，只保留1/2
        crop_img = frame[60:120, 0:160]
        # 将裁减后的图片1转为灰度图像
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        # 对转换的图片进行高斯模糊处理
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # 对模糊处理后的图片进行二值化处理
        ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
        # 使用形态学开操作消除小的黑点
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        # 使用形态学闭操作连接断开的线段
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        # 对二值化处理后的图片进行腐蚀处理
        mask = cv2.erode(closed, None, iterations=2)
        # 膨胀
        dilated = cv2.dilate(mask, None, iterations=2)
        # 在原图像上画出黑线
        image, contours, hierarchy = cv2.findContours(dilated.copy(), 1, cv2.CHAIN_APPROX_NONE)
        return image, contours

    def run(self):
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 160)
        self.cap.set(4, 120)
        # 初始化舵机角度
        self.loborobot.set_servo_angle(10, 90) # 水平舵机  
        self.loborobot.set_servo_angle(9, 150) # 直立舵机

        while self.running:
            if not self.running:
                break       
            # 从摄像头里读取图片
            ret, frame = self.cap.read()
            image, contours = self.process_image(frame)
            if ret:
                # 初始化旋转的开始时间
                start_time = None
                # 初始化是否已经开始旋转的标志
                is_rotating = False
                if len(contours) > 0:
                    # 使用max函数求最大轮廓
                    c = max(contours, key=cv2.contourArea)
                   # 如果轮廓的面积大于阈值
                    if cv2.contourArea(c) > 1000:
                        # 拿到轮廓的矩
                        M = cv2.moments(c)
                        # 计算中心点坐标x， y M['m10']与面积相除到x轴质心，M['m01']与面积相除到y轴质心
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])
                        # 绘制竖线
                        cv2.line(image, (cx, 0), (cx, 720), (255, 0, 0), 1)
                        # 绘制横线
                        cv2.line(image, (0, cy), (1280, cy), (255, 0, 0), 1)
                        # 重置旋转的开始时间和标志
                        start_time = None
                        is_rotating = False
                        # 计算位置误差
                        error = cx - 80  # 假设图像中心在80
                        # 使用PID控制器计算转向角度
                        turn_angle = self.pid.update(error)
                        self.per = (turn_angle/9)*0.01
                        self.handle_turn(error, turn_angle, self.loborobot.turn_right if error > 0 else self.loborobot.turn_left)
                    else:
                        is_rotating, start_time = self.handle_no_path(is_rotating, start_time)
                else:
                    is_rotating, start_time = self.handle_no_path(is_rotating, start_time)

                # 显示图像
                cv2.imshow('frame', image)
                if cv2.waitKey(1) & 0xFF == ord('q') or not self.running:
                    print("stop")
                    self.cap.release()
                    break    
            else:
                print("摄像头打开失败")
                break
            if not self.running:
                    break
        self.cap.release()
        cv2.destroyAllWindows()
        
    def stop(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.running = False


class send_recv_class(Process):
    def __init__(self, conn, queue):
        self.conn = conn
        self.queue = queue
        self.running = True
        super(send_recv_class, self).__init__()

    def run(self) -> None:
        self.conn.send('你可以通过wsad控制小车的方向,通过t切换循迹模式，o切换避障模式,stop停止，输入q退出'.encode())
        time.sleep(2)
        self.conn.send('请发送一条命令。'.encode())
        while self.running:
            data = self.conn.recv(1024)
            print(data.decode())# 打印数据
            if data.decode() in ['w', 's', 'a', 'd', 't', 'o', 'stop']:
                self.conn.send('正在执行，请等待...'.encode())
                if data.decode() == 'w':
                    print('前进')
                    loborobot.turn_up(40, 0.5)  # 控制小车前进S
                    loborobot.music_play('w')
           
                    loborobot.turnstop()
                elif data.decode() == 's':
                    print('后退')
                    loborobot.turn_down(40, 0.5)  # 控制小车后退
                    loborobot.music_play('s')
                 
                    loborobot.turnstop()
                elif data.decode() == 'a':
                    print('左移')
                    loborobot.moveleft(40, 0.5)  # 控制小车左移
                    loborobot.music_play('a')
    
                    loborobot.turnstop()
                elif data.decode() == 'd':
                    print('右移')
                    loborobot.moveright(40, 0.5)  # 控制小车右移
                    loborobot.music_play('d')
    
                    loborobot.turnstop()
                elif data.decode() == 't':
                    print('循迹模式')
                    if self.queue.empty():
                        self.queue.put('track')
                elif data.decode() == 'o':
                    print('避障模式')
                    if self.queue.empty():
                        self.queue.put('obstacle')
                elif data.decode() == 'stop':
                    print('停止')
                    if self.queue.empty():
                        self.queue.put('stop')
                elif data.decode() == 'q':
                    print('退出')
                    self.running = False
                    break            
                self.conn.send('请发送一条命令。'.encode())

    def stop(self):
        self.running = False


if __name__ == '__main__':
   
    loborobot = LOBOROBOT()

    # 创建一个队列用于进程间通信
    queuemodel = Queue()

    obstacle_thread = None  # 初始化为None
    tracking_thread = None  # 初始化为None
    p = None  # 初始化为None
    sock = socket(AF_INET, SOCK_STREAM)
    # bind绑定地址
    sock.bind(('192.168.43.150', pook))
    # 监听队列
    sock.listen(5)
    # 等待连接

    try:
        conn = None  # 初始化连接对象为 None
        while True:
            if conn is None:  # 如果没有当前连接
                print('等待客户端连接')
                conn, addr = sock.accept()  # 接受新的连接
                print('新连接的客户端地址为', addr)
            if p is not None:  # 如果已经有进程在运行
                pass
            else:
                p = send_recv_class(conn, queuemodel)
                p.start()
            while queuemodel.empty():  # 循环等待，直到队列中有数据
                time.sleep(0.1)  # 每次循环之间暂停0.1秒，以减少CPU使用率
            while not queuemodel.empty():  # 循环直到队列为空
                print('模式切换ing')
                flag = queuemodel.get()
                print("flag", flag)
                if flag == 'track':
                    if tracking_thread is not None:
                        tracking_thread.stop()
                        tracking_thread.join(timeout=1.0)  # 等待线程结束
                    if obstacle_thread is not None:
                        obstacle_thread.stop()
                        obstacle_thread.join(timeout=1.0)  # 等待线程结束
                        obstacle_thread = None
                    tracking_thread = TrackingThread(loborobot, flag)
                    tracking_thread.start()
                    # while not queuemodel.empty():
                    #     queuemodel.get_nowait()
                elif flag == 'obstacle':
                    if tracking_thread is not None:
                        tracking_thread.stop()
                        tracking_thread.join(timeout=1.0)  # 等待线程结束
                        tracking_thread = None
                    if obstacle_thread is not None:
                        obstacle_thread.stop()
                        obstacle_thread.join(timeout=1.0)  # 等待线程结束
                    obstacle_thread = ObstacleThread(loborobot, flag)
                    obstacle_thread.start()
                    # while not queuemodel.empty():
                    #     queuemodel.get_nowait()
                elif flag == 'stop':
                    if tracking_thread is not None:
                        tracking_thread.stop()
                        # tracking_thread.join(timeout=1.0)  # 等待线程结束
                        tracking_thread = None
                    if obstacle_thread is not None:
                        obstacle_thread.stop()
                        # obstacle_thread.join(timeout=1.0)  # 等待线程结束
                        obstacle_thread = None
                    loborobot.turnstop()
                    # while not queuemodel.empty():
                    #     queuemodel.get_nowait()
                print('模式切换完成，当前模式是', flag)
            print('等待新模式切换')
    except KeyboardInterrupt:
        print("stop")
        # modelwaitprocess.stop()
        if obstacle_thread is not None:  # 检查是否已经被定义
            obstacle_thread.stop()
        if tracking_thread is not None:
            tracking_thread.stop()

    loborobot.turnstop() # 停止小车
    GPIO.cleanup() # 清理GPIO资源
