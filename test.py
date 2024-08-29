# import threading
# import time

# class ObstacleThread(threading.Thread):
#     def __init__(self, obstacleflag):
#         threading.Thread.__init__(self)
#         self.obstacleflag = obstacleflag
#         self.running = True
#     def run(self):
#         i = 0
#         while self.running:
#             print("running true! :", i)
#             i += 1
#     def stop(self):
#         self.running = False

# if __name__ == '__main__':

#     flag = False
#     while True:
#         # 检测键盘输入值，如果检测到G，则flag设为True
#         key = input()
#         if key == 'G':
#             flag = True
        
#         if flag:
#             break

#     # 创建并启动线程
#     obstacle_thread = ObstacleThread(flag)
#     obstacle_thread.start()
#     # 当键盘输入ctrl+c时，停止线程
#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         obstacle_thread.stop()
import cv2
import numpy as np

def nothing(x):
    pass

# 创建一个窗口
cv2.namedWindow('image')

# 创建滑动条
cv2.createTrackbar('HMin', 'image', 0, 179, nothing)
cv2.createTrackbar('SMin', 'image', 0, 255, nothing)
cv2.createTrackbar('VMin', 'image', 0, 255, nothing)
cv2.createTrackbar('HMax', 'image', 179, 179, nothing)
cv2.createTrackbar('SMax', 'image', 255, 255, nothing)
cv2.createTrackbar('VMax', 'image', 255, 255, nothing)

while True:
    cap = cv2.VideoCapture(0)
    # 更改视频尺寸
    cap.set(3, 320)
    cap.set(4, 320)
    ret, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 获取滑动条的值
    hMin = cv2.getTrackbarPos('HMin', 'image')
    sMin = cv2.getTrackbarPos('SMin', 'image')
    vMin = cv2.getTrackbarPos('VMin', 'image')
    hMax = cv2.getTrackbarPos('HMax', 'image')
    sMax = cv2.getTrackbarPos('SMax', 'image')
    vMax = cv2.getTrackbarPos('VMax', 'image')

    # 创建HSV阈值
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # 提取黄色区域
    mask = cv2.inRange(hsv, lower, upper)

    cv2.imshow('mask', mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()