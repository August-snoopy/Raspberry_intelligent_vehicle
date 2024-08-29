# 用于控制蜂鸣器
import RPi.GPIO as GPIO # type: ignore
import time
global Buzz
# 创建一个蜂鸣器实例
channel = 11
frequency = 440
dc = 50


# 定义三个列表CL，CM，CH，分别对应低音、中音、高音C调的频率
CL = [262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494]
CM = [523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988]
CH = [1046, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976]

# 定义旋律和节奏
song_1 = [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60, 67, 67, 65, 65, 64, 64, 62, 67, 67, 65, 65, 64, 64, 62, 60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60]
beat_1 = [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2]

song_2 = [64, 64, 62, 62, 60, 60, 67, 67, 65, 65, 64, 64, 62, 62, 67, 67, 65, 65, 64, 64, 62, 60, 60, 67, 67, 65, 65, 64, 64, 62, 62, 60, 60, 67, 67, 65, 65, 64, 64, 62, 62, 67, 67, 65, 65, 64, 64, 62]
beat_2 = [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2]

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

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(channel, GPIO.OUT)


def play_song(song, beat):
    for i in range(len(song)):
        pwm.ChangeFrequency(CL[song[i]])
        time.sleep(0.5 * beat[i])

if __name__ == '__main__':
    setup()
    pwm = GPIO.PWM(channel, frequency)
    pwm.start(dc)
    try:
        while True:
            # play_song(song_1, beat_1)
            # time.sleep(1)
            # play_song(song_2, beat_2)
            # time.sleep(1)
            play_song(songP, songT)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()