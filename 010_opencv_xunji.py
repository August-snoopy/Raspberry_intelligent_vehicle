# 使用opencv检测黑线循迹
import cv2
from loborobot import LoboRobot

cap = cv2.VideoCapture(0)
cap.set(3, 160)
cap.set(4, 120)

# 初始化舵机角度
laborobot = LoboRobot()
laborobot.set_angle(10, 90) # 水平舵机  
laborobot.set_angle(9, 90) # 直立舵机

# 按键函数
while True:
    # 从摄像头里读取图片
    ret, frame = cap.read()
    if ret:
        # 对读取到的frame进行裁剪，只保留1/2
        crop_img = frame[60:120, 0:160]
        # 将裁减后的图片1转为灰度图像
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        # 对转换的图片进行高斯模糊处理
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # 对模糊处理后的图片进行二值化处理
        ret, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
        # 对二值化处理后的图片进行腐蚀处理
        mask = cv2.erode(thresh, None, iterations=2)
        # 膨胀
        dilated = cv2.dilate(mask, None, iterations=2)
        # 在原图像上画出黑线
        contours, hierarchy = cv2.findContours(dilated.copy(), 1, cv2.CHAIN_APPROX_NONE)

        if len(contours) > 0:
            # 使用max函数求最大轮廓
            c = max(contours, key=cv2.contourArea)
            # 拿到轮廓的矩
            M = cv2.moments(c)
            # 计算中心点坐标x， y M['m10']与面积相除到x轴质心，M['m01']与面积相除到y轴质心
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            # 绘制竖线
            cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
            # 绘制横线
            cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
            # 裁剪后的图像像素是 0-160，
            if cx >= 120:
                # 中心点在图像右侧，向右转
                print("中心点在图像右侧，向右转")
                laborobot.set_angle(10, 90)
                laborobot.set_angle(9, 90)
            elif cx < 120 and cx > 50:
                # 中心点在图像中间，直行
                print("中心点在图像中间，直行!")
                laborobot.set_angle(10, 90)
                laborobot.set_angle(9, 90)
            else:
                # 中心点在图像左侧，向左转
                print("中心点在图像左侧，向左转")
                laborobot.set_angle(10, 90)
                laborobot.set_angle(9, 90)
        else:
            print("未检测到黑线")
            laborobot.set_angle(10, 90)
            laborobot.set_angle(9, 90)
        cv2.imshow('frame', crop_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("stop")
            break    
    else:
        print("摄像头打开失败")
        break

