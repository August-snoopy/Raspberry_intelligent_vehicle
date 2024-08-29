# opencv手势识别
import cv2
import numpy as np
import math

def hand_gesture_recognition(cap):
    while True:
        try:
            ret, frame = cap.read()
            # 沿y轴镜像翻转
            frame = cv2.flip(frame, 1)
            roi = frame[0:300, 0:300]
            # bgr hsv灰度图
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            # 定义阈值，拿到对应肤色的手
            lower_skin = np.array([0, 10, 70], dtype=np.uint8)
            upper_skin = np.array([30, 255, 255], dtype=np.uint8)

            # 提取手势图像
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            # 形态学处理，膨胀
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=2)
            # 高斯模糊
            mask = cv2.GaussianBlur(mask, (3, 3), 50)
            # 找到手势轮廓
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # 找到最大轮廓
            cnt = max(contours, key=lambda x: cv2.contourArea(x))
            # 计算周长
            epsilon = cv2.arcLength(cnt, True)*0.0005
            # 多边形轮廓
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            # 找到包含凸包顶点的轮廓
            hull = cv2.convexHull(cnt)
            # 计算凸包和手轮廓的面积
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)
            # 查找凸包中未被手势覆盖的面积
            arearatio = ((areahull - areacnt) / areacnt) * 100
            # 计算近似多边形凸包，返回凸包索引
            hull = cv2.convexHull(approx, returnPoints = False)
            # 找到凸包相对于手的缺陷,返回的是数组，包含了四个内容，起点索引，结束点索引，最远点索引，缺陷深度
            defects = cv2.convexityDefects(approx, hull)
            # 计数
            count_defects = 0
            # 遍历所有的凸包缺陷
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(approx[s][0])
                end = tuple(approx[e][0])
                far = tuple(approx[f][0])
                # 计算三角形的三边长度
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                # 通过海伦公式求三角形面积
                s = (a + b + c) / 2
                ar = math.sqrt(s * (s - a) * (s - b) * (s - c))
                # 计算手指到凸包的距离
                d = (2 * ar) / a
                # 计算角度
                angle = math.acos((c ** 2 + b ** 2 - a ** 2) / (2 * c * b))*58
                
                # 忽略小角度
                if angle <= 90 and d > 30:
                    count_defects += 1
                    cv2.circle(roi, far, 3, [255, 0, 0], -1)
                cv2.line(roi, start, end, [0, 255, 0], 2)
            # 打印手势
            if count_defects == 0:
                cv2.putText(frame, 'ONE', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
            elif count_defects == 1:
                cv2.putText(frame, 'TWO', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
            elif count_defects == 2:
                cv2.putText(frame, 'THREE', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
            elif count_defects == 3:
                cv2.putText(frame, 'FOUR', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
            elif count_defects == 4:
                cv2.putText(frame, 'FIVE', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

            # 显示视频
            cv2.imshow('frame', frame)
            cv2.imshow('mask', mask)

            # 按下'q'键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(e)
            break

    cap.release()
    cv2.destroyAllWindows()

def detect_yellow_ball(cap):
    no_ball_counter = 0  # 添加一个没有检测到小球的帧的计数器
    ball_count = 0  # 将小球的数量的初始化放在循环外面
    while True:
        try:
            ret, frame = cap.read()
            # 转换到HSV色彩空间
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # 定义黄色的阈值
            lower_yellow = np.array([10, 125, 125], dtype=np.uint8)
            upper_yellow = np.array([30, 255, 255], dtype=np.uint8)
            # 提取黄色区域
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            # 对结果进行一些形态学操作，例如膨胀和腐蚀，以去除噪声
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            # 使用Hough圆变换来检测球形物体
            circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 30, param1=70, param2=20, minRadius=5, maxRadius=100)
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                    cv2.rectangle(frame, (x-r, y-r), (x+r, y+r), (0, 255, 0), 2)  # 画出小球的矩形框
                if len(circles) >= ball_count:  # 如果检测到的小球数量大于等于上一帧的数量，那么更新小球的数量
                    ball_count = len(circles)
                no_ball_counter = 0  # 如果检测到小球，那么将没有检测到小球的帧的计数器重置为0
            else:
                no_ball_counter += 1  # 如果没有检测到小球，那么将没有检测到小球的帧的计数器加1
                if no_ball_counter > 10:  # 如果连续10帧都没有检测到小球，那么将小球的数量设置为0
                    ball_count = 0
            cv2.putText(frame, 'Balls: {}'.format(ball_count), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)  # 在帧上打印出小球的数量
            cv2.imshow('frame', frame)
            cv2.imshow('mask', mask)
            # 按下'q'键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(e)
            break
    cap.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    # 更改视频尺寸
    cap.set(3, 320)
    cap.set(4, 320)
    # hand_gesture_recognition(cap)
    detect_yellow_ball(cap)




