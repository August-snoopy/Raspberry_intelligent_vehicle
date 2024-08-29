#opencv手势识别
import math

import cv2
import numpy as np

cap=cv2.VideoCapture(0)
#更改视频的尺寸
cap.set(3,320)
cap.set(4,320)

#循环拿到视频帧  处理 识别对应的手势

while True:
    #当发生异常  excpet捕捉异常

    try:
        ret,frame=cap.read()
        #flip()    参数1 沿y轴反转  0沿x轴反转
        frame=cv2.flip(frame,1)
        roi=frame[0:300,0:300]
        #bgr hsv灰度图
        hsv=cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        #定义阈值  拿到肤色的手
        lower=np.array([0,20,70],dtype=np.uint8)
        upper=np.array([20,255,255],dtype=np.uint8)
        #提取手势图像,
        mask=cv2.inRange(hsv,lower,upper)
        #形态处理 膨胀 膨胀4次
        mask=cv2.dilate(mask,np.ones((3,3),dtype=np.uint8),iterations=4)
        #高斯模糊  5,5    100
        mask=cv2.GaussianBlur(mask,(5,5),100)
        #找手势轮廓
        contours,his=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        #取最大的面积轮廓
        cnt=max(contours,key=lambda x:cv2.contourArea(x))
        #拿到原始轮廓信息 计算周长
        epsilon=cv2.arcLength(cnt,True)*0.0005
        #多边形轮廓
        approx=cv2.approxPolyDP(cnt,epsilon,True)
        #围绕手的做凸包 包含凸包顶点的轮廓
        hull=cv2.convexHull(cnt)
        #计算凸包和手轮廓的面积
        areahull=cv2.contourArea(hull)
        areacnt=cv2.contourArea(cnt)
        #查找凸包中未被手覆盖的面积所占百分比
        arearatio=((areahull-areacnt)/areacnt)*100
        #计算近似多边形的凸包 返回凸包的索引
        hull=cv2.convexHull(approx,returnPoints=False)
        # 拿到凸包相对于手的缺陷  返回缺陷信息
        #返回值是数组 包含所有的缺陷信息
        #每个缺陷包含了4个内容 起点索引 结束点索引，最远点索引，缺陷深度
        defacts=cv2.convexityDefects(approx,hull)
        #通过缺陷信息 来计算缺陷角度
        #定义默认手势0
        l=0
        # 循环拿缺陷 如果有缺陷加1 循环完  返回
        # shape  [3,2]   数组有3个数据   每个数据有2个值
        for i in range(defacts.shape[0]):
            s,e,f,d=defacts[i,0]
            start=tuple(approx[s][0])
            end=tuple(approx[e][0])
            far=tuple(approx[f][0])
            #求三个边的边长
            a=math.sqrt((end[0]-start[0])**2+(end[1]-start[1])**2)
            b=math.sqrt((far[0]-start[0])**2+(far[1]-start[1])**2)
            c=math.sqrt((end[0]-far[0])**2+(end[1]-far[1])**2)
            #通过海伦公式求面积
            s=(a+b+c)/2
            ar=math.sqrt(s*(s-a)*(s-b)*(s-c))
            #计算点到凸包之间的距离
            d=(2*ar)/a
            #通过余玄规则 余玄值->弧度->角度  1弧度pi/180
            angle=math.acos((b**2+c**2-a**2)/(2*b*c))*58
            if angle<=90 and d>30:
                l+=1
                cv2.circle(roi,far,3,[255,0,0],-1)
            #在手周围划线
            cv2.line(roi,start,end,[0,255,0],2)
        l+=1
        print(l)

        cv2.imshow('frame',frame)
        cv2.imshow('mask',mask)

    except Exception as e:
        print(e)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break

