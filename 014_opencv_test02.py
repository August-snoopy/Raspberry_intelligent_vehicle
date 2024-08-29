#opencv 边缘检测
import cv2
cap=cv2.VideoCapture(0)

while True:
    ret,frame=cap.read()
    grey=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(grey,(5,5),0)
    #边缘检测
    cannys=cv2.Canny(blur,50,150)
    cnts=cv2.findContours(cannys,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
    cv2.drawContours(frame,cnts,-1,(0,255,0),2)
    for con in cnts:
        #大于500认为是障碍
        area=cv2.contourArea(con)
        if area>500:
            #计算轮廓中心
            M = cv2.moments(con)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            # 图像上绘制点
            cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)
            if cx < frame.shape[1] / 2 - 30:
                print('向右')
            elif cx > frame.shape[1] / 2 + 30:
                print('向左')
            else:
                print('停止')

    cv2.imshow('frame',frame)
    cv2.imshow('canny',cannys)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break