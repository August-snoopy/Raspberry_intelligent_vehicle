import RPi.GPIO as GPIO # type: ignore
import smbus # type: ignore
import time
import math

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
    
    # 测试4号电机旋转
    def up(self, speed, t):
        '''
        :param speed:   占空比，表示小车速度
        :param t:       旋转方向，1为正向，0为反向
        '''
        self.pwm.setdutycycle(self.PWMD, speed)
        if t == 1:
            GPIO.output(self.DIN1, 0)
            GPIO.output(self.DIN2, 1)
            time.sleep(3)
            GPIO.cleanup()
        else:
            GPIO.output(self.DIN1, 1)
            GPIO.output(self.DIN2, 0)
            time.sleep(3)
            GPIO.cleanup()

    # 测试前三个任意一个电机运功
    def up_1(self, speed, t, i):
        """
        :param speed:   占空比，表示小车速度
        :param t:       旋转方向，1为正向，0为反向
        """
        if i == 1:
            self.pwm.setdutycycle(self.PWMA, speed)
            if t == 1:
                self.pwm.setlevel(self.AIN1, 0)
                self.pwm.setlevel(self.AIN2, 1)
                time.sleep(3)
                self.pwm.setdutycycle(self.PWMA, 0)
            else:
                self.pwm.setlevel(self.AIN1, 1)
                self.pwm.setlevel(self.AIN2, 0)
                time.sleep(3)
                self.pwm.setdutycycle(self.PWMA, 0)
        if i == 2:
            self.pwm.setdutycycle(self.PWMB, speed)
            if t == 1:
                self.pwm.setlevel(self.BIN1, 1)
                self.pwm.setlevel(self.BIN2, 0)
                time.sleep(3)
                self.pwm.setdutycycle(self.PWMB, 0)
            else:
                self.pwm.setlevel(self.BIN1, 0)
                self.pwm.setlevel(self.BIN2, 1)
                time.sleep(3)
                self.pwm.setdutycycle(self.PWMB, 0)
        if i == 3:
            self.pwm.setdutycycle(self.PWMC, speed)
            if t == 1:
                self.pwm.setlevel(self.CIN1, 1)
                self.pwm.setlevel(self.CIN2, 0)
                time.sleep(3)
                self.pwm.setdutycycle(self.PWMC, 0)
            else:
                self.pwm.setlevel(self.CIN1, 0)
                self.pwm.setlevel(self.CIN2, 1)
                time.sleep(3)
                self.pwm.setdutycycle(self.PWMC, 0)

    # 前进
    def forward(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 0)
        self.pwm.setlevel(self.AIN2, 1)
        self.pwm.setlevel(self.BIN1, 1)
        self.pwm.setlevel(self.BIN2, 0)

        self.pwm.setlevel(self.CIN1, 1)
        self.pwm.setlevel(self.CIN2, 0)
        GPIO.output(self.DIN1, 0)
        GPIO.output(self.DIN2, 1)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
    # 后退
    def back(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 1)
        self.pwm.setlevel(self.AIN2, 0)
        self.pwm.setlevel(self.BIN1, 0)
        self.pwm.setlevel(self.BIN2, 1)

        self.pwm.setlevel(self.CIN1, 0)
        self.pwm.setlevel(self.CIN2, 1)
        GPIO.output(self.DIN1, 1)
        GPIO.output(self.DIN2, 0)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0) 
    
    # 左转
    def left(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 1)
        self.pwm.setlevel(self.AIN2, 0)
        self.pwm.setlevel(self.BIN1, 1)
        self.pwm.setlevel(self.BIN2, 0)

        self.pwm.setlevel(self.CIN1, 1)
        self.pwm.setlevel(self.CIN2, 0)
        GPIO.output(self.DIN1, 1)
        GPIO.output(self.DIN2, 0)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)

    # 右移
    def right(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 0)
        self.pwm.setlevel(self.AIN2, 1)
        self.pwm.setlevel(self.BIN1, 0)
        self.pwm.setlevel(self.BIN2, 1)

        self.pwm.setlevel(self.CIN1, 0)
        self.pwm.setlevel(self.CIN2, 1)
        GPIO.output(self.DIN1, 0)
        GPIO.output(self.DIN2, 1)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
    
    # 左转
    def turnleft(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 1)
        self.pwm.setlevel(self.AIN2, 0)
        self.pwm.setlevel(self.BIN1, 1)
        self.pwm.setlevel(self.BIN2, 0)

        self.pwm.setlevel(self.CIN1, 0)
        self.pwm.setlevel(self.CIN2, 1)
        GPIO.output(self.DIN1, 0)
        GPIO.output(self.DIN2, 1)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
    
    # 右转
    def turnright(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 0)
        self.pwm.setlevel(self.AIN2, 1)
        self.pwm.setlevel(self.BIN1, 0)
        self.pwm.setlevel(self.BIN2, 1)

        self.pwm.setlevel(self.CIN1, 1)
        self.pwm.setlevel(self.CIN2, 0)
        GPIO.output(self.DIN1, 1)
        GPIO.output(self.DIN2, 0)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
    
    # 前左斜
    def forward_left(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 0)
        self.pwm.setlevel(self.AIN2, 0)
        self.pwm.setlevel(self.BIN1, 1)
        self.pwm.setlevel(self.BIN2, 0)

        self.pwm.setlevel(self.CIN1, 1)
        self.pwm.setlevel(self.CIN2, 0)
        GPIO.output(self.DIN1, 0)
        GPIO.output(self.DIN2, 0)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
    
    # 前右斜
    def forward_right(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 0)
        self.pwm.setlevel(self.AIN2, 1)
        self.pwm.setlevel(self.BIN1, 0)
        self.pwm.setlevel(self.BIN2, 0)

        self.pwm.setlevel(self.CIN1, 0)
        self.pwm.setlevel(self.CIN2, 0)
        GPIO.output(self.DIN1, 0)
        GPIO.output(self.DIN2, 1)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
    
    # 左后斜
    def back_left(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 1)
        self.pwm.setlevel(self.AIN2, 0)
        self.pwm.setlevel(self.BIN1, 0)
        self.pwm.setlevel(self.BIN2, 0)

        self.pwm.setlevel(self.CIN1, 0)
        self.pwm.setlevel(self.CIN2, 0)
        GPIO.output(self.DIN1, 1)
        GPIO.output(self.DIN2, 0)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)

    # 右后斜
    def back_right(self, speed):
        self.pwm.setdutycycle(self.PWMA, speed)
        self.pwm.setdutycycle(self.PWMB, speed)
        self.pwm.setdutycycle(self.PWMC, speed)
        self.pwm.setdutycycle(self.PWMD, speed)
        self.pwm.setlevel(self.AIN1, 0)
        self.pwm.setlevel(self.AIN2, 0)
        self.pwm.setlevel(self.BIN1, 0)
        self.pwm.setlevel(self.BIN2, 1)

        self.pwm.setlevel(self.CIN1, 0)
        self.pwm.setlevel(self.CIN2, 1)
        GPIO.output(self.DIN1, 0)
        GPIO.output(self.DIN2, 0)
        time.sleep(1)
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)

    # 停止
    def stop(self):
        self.pwm.setdutycycle(self.PWMA, 0)
        self.pwm.setdutycycle(self.PWMB, 0)
        self.pwm.setdutycycle(self.PWMC, 0)
        self.pwm.setdutycycle(self.PWMD, 0)
        GPIO.cleanup()

if __name__ == '__main__':
    l = LOBOROBOT()
    # for i in range(0, 4):
    #     if i == 0:
    #         l.up(50, 1)
    #     else:
    #         l.up_1(50, 1, i)
    for i in range(0, 11):
        if i == 0:
            l.forward(50)         
        if i == 1:
            l.back(50)
        if i == 2:
            l.left(50)
        if i == 3:
            l.right(50) 
        if i == 4:
            l.turnleft(50)
        if i == 5:
            l.turnright(50)
        if i == 6:
            l.forward_left(50)
        if i == 7:
            l.forward_right(50)
        if i == 8:
            l.back_left(50)
        if i == 9:
            l.back_right(50)
        if i == 10:
            l.stop()