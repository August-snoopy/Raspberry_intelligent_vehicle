# 用于使用按键点亮树莓派小车的LED灯

# 按下绿灯亮，松开按钮红灯亮
import RPi.GPIO as GPIO # type: ignore
import time

# 实例按钮 绿灯和红灯的接口
btnpin = 19
gpin = 5
rpin = 6

#设置对应按钮和灯对应的模式 输入或者输出
def setup():
    GPIO.setwarnings(False)
    # 设置引脚编码类型
    GPIO.setmode(GPIO.BCM)
    # 设置对应按钮和等连接的引脚模式 
    GPIO.setup(gpin, GPIO.OUT)
    GPIO.setup(rpin, GPIO.OUT)
    # 按钮输入模式
    GPIO.setup(btnpin,GPIO.IN)

if __name__ == '__main__':
    # 初始化
    setup()
    # 循环检测按钮的状态 高电平或者低电平
    # 按钮是高电平 为按压状态 此时亮绿灯
    # 否则 亮红灯
    try:
        while True:
            # 检测按键
            if GPIO.input(btnpin) == True:
                time.sleep(0.1)
                if GPIO.input(btnpin) == True:
                    GPIO.output(gpin, 0)
                    GPIO.output(rpin, 1)
            elif GPIO.input(btnpin) == False:
                time.sleep(0.1)
                if GPIO.input(btnpin) == False:
                    GPIO.output(gpin, 1)
                    GPIO.output(rpin, 0)    
    except KeyboardInterrupt:
        GPIO.cleanup()



