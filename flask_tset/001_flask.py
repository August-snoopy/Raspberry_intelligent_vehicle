# 一个简单的flask服务器测试
from flask import Flask, json, request
import cv2
from pyzbar import pyzbar
import base64
import numpy as np
from ultralytics import YOLO


# 声明一个flask应用
app = Flask(__name__)
@app.route('/')
@app.route('/index')
def hello_world():
    return "hello world"

@app.route('/test', methods = {"POST"})
def main():
    # 将接收的字节流数据解码为字符串
    data = request.get_data().decode()
    data = json.loads(data)
    print(data)
    return '1'

@app.route('/qr', methods = {"POST"})
#二维码处理的函数
def read_qr():
    data = request.get_data().decode() # json格式
    data = json.loads(data)  # 字典格式
    image_b64 = data['img'] # base64编码的图片
    image = base64.b64decode(image_b64) # 一个字符串的数组
    nparr = np.frombuffer(image, np.uint8)  # 一个jpg的数组
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # frame的数组
    barcodes = pyzbar.decode(img)
    data = 'None'
    for barcode in barcodes:
        #提取二维码数据
        data = barcode.data.decode('utf-8')
    return data

@app.route('/yolo', methods = {"POST"})
def yolo():
    # 加载模型
    model = YOLO(model=r'yolov8n.pt')
    # 读取图片
    data = request.get_data().decode() # json格式
    data = json.loads(data)  # 字典格式
    image_b64 = data['img'] # base64编码的图片
    image = base64.b64decode(image_b64) # 一个字符串的数组
    nparr = np.frombuffer(image, np.uint8)  # 一个jpg的数组
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # frame的数组
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
    return results

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8000, debug = True)
