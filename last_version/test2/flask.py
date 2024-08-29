import base64
import json
from flask import Flask, request
import numpy as np
import cv2
from pyzbar import pyzbar
from ultralytics import YOLO

# 预加载YOLO模型
model_light = YOLO('D:/Augustine/code/python_projects/intelligent_car_code/last_version/best_light.pt')
model_sign = YOLO('D:/Augustine/code/python_projects/intelligent_car_code/last_version/best_sign.pt')

# 声明一个flask应用
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return 'hello_world'

@app.route('/test', methods=['POST'])
def process_image():
    data = request.get_data().decode()  # 结果json
    data = json.loads(data)  # 结果格式 字典
    image_b64 = data['img']  # 结果  base64编码的图片
    image_dacode = base64.b64decode(image_b64)  # 结果 字符串的数组
    nparr = np.frombuffer(image_dacode, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    light_result = process_light(image)
    qr_result = read_qr(image)
    sign_result = process_sign(image)

    return {'light': light_result, 'qr': qr_result, 'sign': sign_result}

def process_light(image):
    results = predict(image, model_light)
    for result in results:
        if float(result['conf']) > 0.4:
            if result['class_name'] == 'red':
                return 1
            elif result['class_name'] == 'yellow':
                return 2
            elif result['class_name'] == 'green':
                return 3
    return 0

def process_sign(image):
    results = predict(image, model_sign)
    for result in results:
        if float(result['conf']) > 0.4:
            if result['class_name'] in ['40 Limit', '50 Limit', '60 Limit', '70 Limit', '80 Limit']:
                return result['class_name']
    return ''

def read_qr(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        return barcode.data.decode('utf-8')
    return 'None'

def predict(image, model):
    pred = model(image)
    results = []
    for res in pred:
        for box in res.boxes:
            class_id = int(box.cls.cpu())
            bbox = box.xyxy[0].squeeze().tolist()
            result = {
                'class_name': res.names[class_id],
                'bbox': bbox,
                'class_id': class_id,
                'conf': box.conf[0].squeeze().tolist()
            }
            results.append(result)
    return results

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)