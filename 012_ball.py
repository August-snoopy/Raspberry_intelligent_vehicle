#球体识别
import cv2
import numpy as np

cap=cv2.VideoCapture(0)
cap.set(3,360)
cap.set(4,360)
#定义橙黄色阈值hsv
ball_lower=np.array([10,150,150])
ball_max=np.array([30,255,255])
while True:
    try:
        ret,frame=cap.read()
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask=cv2.inRange(hsv,ball_lower,ball_max)
        mask=cv2.erode(mask,None,iterations=2)
        mask=cv2.dilate(mask,None,iterations=2)
        mask=cv2.GaussianBlur(mask,(3,3),0)
        cnts=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        print(cnts)
        if len(cnts)>0:
            cnt=max(cnts,key=cv2.contourArea)
            print(cnt)
            (x,y),r=cv2.minEnclosingCircle(cnt)
            if int(r)>30:
                cv2.circle(frame,(int(x),int(y)),int(r),(0,255,0),2)
                print('停车')
                print('向左或者向右避开障碍')
            else:
                cv2.circle(frame, (int(x), int(y)), int(r), (0, 0, 255), 2)
                print('继续行进')
                h_x_min=frame.shape[1]/2-30
                h_x_max=frame.shape[1]/2+30
                if x<h_x_min:
                    print('向右避开障碍')
                elif x>h_x_max:
                    print('向左避开障碍')
                else:
                    print('正前方发现障碍，选择行进方式')


        cv2.imshow('mask',mask)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1)&0xFF==ord('q'):
            break
    except Exception as e:
        print(e)

# 练习     opencv检测障碍  不知道障碍的形状 ，只知道颜色
#         捕捉轮廓   判断小车的障碍检测及行进方式

