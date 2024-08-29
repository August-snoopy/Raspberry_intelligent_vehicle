#coding:utf-8
# 导入UI模块
import tkinter as Tkinter
import RPi.GPIO as GPIO
import time
# 定义音调频率
# C调低音
CL = [0, 131, 147, 165, 175, 196, 211, 248] 
# C调中音
CM = [0, 262, 294, 330, 350, 393, 441, 495]   
# C调高音
CH = [0, 525, 589, 661, 700, 786, 882, 990]  
# 定义乐谱
# 音调 0表示休止符
songP = [
    CM[1],CM[2],CM[3],CM[5],CM[5],CM[0],CM[3],CM[2],CM[1],CM[2],CM[3],CM[0],
    CM[1],CM[2],CM[3],CM[7],CH[1],CH[1],CH[1],CM[7],CH[1],CM[7],CM[6],CM[5],CM[0],
    CM[1],CM[2],CM[3],CM[5],CM[5],CM[0],CM[3],CM[2],CM[1],CM[2],CM[1],CM[0],
    CM[1],CM[2],CM[3],CM[5],CM[1],CM[0],CM[1],CL[7],CL[6],CL[7],CM[1],CM[0]
]
# 音调对应的节拍
songT = [
    2,2,2,1,5,4,2,2,2,1,5,4,
    2,2,2,1,5,2,2,2,1,3,2,4,4,
    2,2,2,1,5,4,2,2,2,1,3,5,
    2,2,2,1,5,4,2,2,2,2,8,2
]
# 定义标准节拍时间
metre = 0.125
# 初始化要使用的引脚
io = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(io, GPIO.OUT)
pwm = GPIO.PWM(io, 440)
# 开始设置占空比为100 则无缘蜂鸣器不会发声
pwm.start(100)
# 播放示例乐曲的方法
def playSong():
    # 修改占空比为50 此时频率生效
    pwm.ChangeDutyCycle(50)
    # 遍历所有音调
    for i in range(0, len(songP)):
        # 0表示休止 禁声
        if songP[i] == 0:
            pwm.ChangeDutyCycle(100)
        # 更改频率控制音调
        else:
            pwm.ChangeDutyCycle(50)
            pwm.ChangeFrequency(songP[i])
        # 通过节拍控制播放时间
        time.sleep(songT[i] * metre) 
    # 禁声
    pwm.ChangeDutyCycle(100)
# 分别播放各个音阶的方法
def playDo():
    pwm.ChangeDutyCycle(50)
    pwm.ChangeFrequency(CM[1])
    time.sleep(0.5)
    pwm.ChangeDutyCycle(100)
def playRe():
    pwm.ChangeDutyCycle(50)
    pwm.ChangeFrequency(CM[2])
    time.sleep(0.5)
    pwm.ChangeDutyCycle(100)
def playMi():
    pwm.ChangeDutyCycle(50)
    pwm.ChangeFrequency(CM[3])
    time.sleep(0.5)
    pwm.ChangeDutyCycle(100)
def playFa():
    pwm.ChangeDutyCycle(50)
    pwm.ChangeFrequency(CM[4])
    time.sleep(0.5)
    pwm.ChangeDutyCycle(100)
def playSo():
    pwm.ChangeDutyCycle(50)
    pwm.ChangeFrequency(CM[5])
    time.sleep(0.5)
    pwm.ChangeDutyCycle(100)
def playLa():
    pwm.ChangeDutyCycle(50)
    pwm.ChangeFrequency(CM[6])
    time.sleep(0.5)
    pwm.ChangeDutyCycle(100)
def playXi():
    pwm.ChangeDutyCycle(50)
    pwm.ChangeFrequency(CM[7])
    time.sleep(0.5)
    pwm.ChangeDutyCycle(100)
# UI相关设置
# 主页面设置
top = Tkinter.Tk()
top.geometry('360x300')
top.minsize(420, 300) 
top.maxsize(420, 300)
top.title("自制电子琴")
l = Tkinter.Label(top, text='自制电子琴', font=('Arial', 18), width=30, height=2)
l.pack()
# UI上的按钮布局
songBtn = Tkinter.Button(top, text="示例歌曲：花海", command=playSong)
songBtn.place(x=30,y=30,width=120,height=40)
doBtn = Tkinter.Button(top,bitmap="gray50", text="Do", compound=Tkinter.LEFT, command=playDo)
doBtn.place(x=0,y=105,width=60,height=200)
reBtn = Tkinter.Button(top,bitmap="gray50", text="Re", compound=Tkinter.LEFT, command=playRe)
reBtn.place(x=60,y=105,width=60,height=200)
miBtn = Tkinter.Button(top,bitmap="gray50", text="Mi", compound=Tkinter.LEFT, command=playMi)
miBtn.place(x=120,y=105,width=60,height=200)
faBtn = Tkinter.Button(top,bitmap="gray50", text="Fa", compound=Tkinter.LEFT, command=playFa)
faBtn.place(x=180,y=105,width=60,height=200)
soBtn = Tkinter.Button(top,bitmap="gray50", text="So", compound=Tkinter.LEFT, command=playSo)
soBtn.place(x=240,y=105,width=60,height=200)
laBtn = Tkinter.Button(top,bitmap="gray50", text="La", compound=Tkinter.LEFT, command=playLa)
laBtn.place(x=300,y=105,width=60,height=200)
xiBtn = Tkinter.Button(top,bitmap="gray50", text="Xi", compound=Tkinter.LEFT, command=playXi)
xiBtn.place(x=360,y=105,width=60,height=200)
stopButton = Tkinter.Button(top, text="关闭")
stopButton.place(x=340,y=30,width=60,height=40)
# 进入消息循环
top.mainloop()