#opencv视觉避障
import cv2
import numpy as np

cap=cv2.VideoCapture(0)
cap.set(3,360)
cap.set(4,360)
#定义白阈值hsv
ball_lower=np.array([0,0,180])
ball_max=np.array([180,30,220])
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
        for cnt in cnts:
            #计算轮廓的面积
            area=cv2.contourArea(cnt)
            if area>500:
                M=cv2.moments(cnt)
                cx=int(M['m10']/M['m00'])
                cy=int(M['m01']/M['m00'])
                #图像上绘制点
                cv2.circle(frame,(cx,cy),5,(0,255,255),-1)
                if cx<frame.shape[1]/2-30:
                    print('向右')
                elif cx>frame.shape[1]/2+30:
                    print('向左')
                else:
                    print('停止')


        cv2.imshow('mask',mask)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1)&0xFF==ord('q'):
            break
    except Exception as e:
        print(e)

# 练习     opencv检测障碍  不知道障碍的形状 ，只知道颜色
#         捕捉轮廓   判断小车的障碍检测及行进方式

