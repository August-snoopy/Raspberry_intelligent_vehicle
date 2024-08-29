# 客户端，用于测试flask服务器
import requests
from flask import json
import cv2
import base64

if __name__ == '__main__':
    cap=cv2.VideoCapture(0)
    ret, frame=cap.read()
    # 初始计算值
    i = 0
    # 帧数
    j = 60
    while ret:
        ret, frame=cap.read()
        # 每十帧取一次
        if i%j == 0:    
            # 将每一帧转换为JPG格式的字节流
            ret , jpg = cv2.imencode('.jpg', frame)
            jpg_bytes = jpg.tobytes()
            # 为了保证数据的完整性和安全性，base64编码
            # base64编码的图片数据字符串
            base64_data = base64.b64encode(jpg_bytes).decode()
            data = {'img': base64_data}
            r = requests.post('http://192.168.43.10:8000/yolo', data = json.dumps(data))
            # print(r.status_code)
            print(r.text)
        i += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
       


# # 用request模拟浏览器客户端向web服务器发送请求
# r = requests.get('https://www.python.org')
# print(r.status_code) # 拿到状态码
# # print(r.json()) # 拿到返回响应的json格式数据
# print(r.text) # 拿到响应的文本数据
# print(r.content) # 拿到响应返回的二进制数据
# print(r.url) # 拿到请求的路由地址

# data = {'img':'123456789'}
# # 测试访问自己的服务器拿到返回值
# r = requests.post('http://192.168.43.10:8000/test', data = json.dumps(data))
# print(r.status_code) # 拿到状态码
# # print(r.json()) # 拿到返回响应的json格式数据
# print(r.text) # 拿到响应的文本数据
# print(r.content) # 拿到响应返回的二进制数据
# print(r.json())
# print(r.url) # 拿到请求的路由地址