import cv2
from ultralytics import YOLO
# 加载模型
model = YOLO(model=r'yolov8n.pt')
# 读取图片
img = cv2.imread(r'YOLO_test\ultralytics-8.2.79\ultralytics\assets\bus.jpg')
# 通过模型进行预测
results = model(img)
# 处理预测结果
for result in results:
    boxes = result.boxes
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0] # 获取检测框坐标
        conf = box.conf[0] # 置信度
        c_id = box.cls[0] # 类别id
        c_name = result.names[int(c_id)] # 类别名称
        print(f'{c_name} {conf:.2f} {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f}')
        # 将检测框画到图上
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(img, f'{c_name} {conf:.2f}', (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # 显示图片
    cv2.imshow('result', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 将上述代码封装为方法
# 测试树莓派小车通过图片发送给flask服务器识别，拿到对应结果



