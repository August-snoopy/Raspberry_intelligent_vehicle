#flask服务器测试
# from requests import request
import base64
import json
import time
import threading
from pyzbar import pyzbar
# from yolo_v8_model import YOLOv8_Detector
import numpy as np
from  flask import Flask,request
import cv2
from  ultralytics import  YOLO
#预加载YOLOv8模型model_light=YOLOv8_Detector()
# model_light.load_model(abs_path('best.pt',path_type='current'))
#
model=YOLO('D:/Augustine/code/python_projects/intelligent_car_code/last_version/best_light.pt')
model_sign=YOLO('D:/Augustine/code/python_projects/intelligent_car_code/last_version/best_sign.pt')
# model_sign=YOLO('D:/BaiduNetdiskDownload/runs-sign/detect/train_v8_sign/weights/best.pt')
#1.声明一个flask应用
app=Flask(__name__)
@app.route('/')
@app.route('/index')
def hello_world():
    return 'hello_world'
@app.route('/test',methods=['POST'])
def main():
    data=request.get_data().decode()#结果json

    data=json.loads(data)#结果格式 字典

    # print(data)
    image_b64=data['img']#结果  base64编码的图片
    image_dacode=base64.b64decode(image_b64)#结果 字符串的数组
    nparr=np.frombuffer(image_dacode,np.uint8)
    image=cv2.imdecode(nparr,cv2.IMREAD_COLOR)


    x=postprocess(image)
    print(x)
    x_result = 0
    y=read_qr(image)
    print(y)
    z=read_sign(image)
    print(z)
    z_result = ''

    if x:
        for i in x:
            if float(i['conf']) > 0.4:
                if i['class_name']=='red':
                        print('识别red')
                        print(int(i['conf']))
                        x_result=1
                if i['class_name']=='yellow':
                        print('识别yellow')
                        x_result = 2
                if i['class_name'] == 'green':
                        print('识别green')
                        x_result = 3
    else:
        x_result=0
    if z:
        for i in z:
            if float(i['conf']) > 0.4:
                if i['class_name'] == '40 Limit':
                    print('限速四十')
                    print(int(i['conf']))
                    z_result = '限速四十'
                if i['class_name'] == '50 Limit':
                    print('限速五十')
                    print(int(i['conf']))
                    z_result = '限速五十'
                if i['class_name'] == '60 Limit':
                    print('限速六十')
                    print(int(i['conf']))
                    z_result = '限速六十'
                if i['class_name'] == '70 Limit':
                    print('限速七十')
                    print(int(i['conf']))
                    z_result = '限速七十'
                if i['class_name'] == '80 Limit':
                    print('限速八十')
                    print(int(i['conf']))
                    z_result = '限速八十'
    else:
        z_result=''
        # return '未识别信号灯'
    # if z:
    #     for i in z:
    #         if i['class_name']=='40 Limit':
    #             if float(i['conf'])>0.4:
    #                 print('限速40')
    #                 print(int(i['conf']))
    #     for i in x:
    #         if i['class_name']=='50 Limit':
    #             print('识别yellow')
    #             # return '识别yellow'
    #     for i in x:
    #         if i['class_name'] =='60 Limit':
    #             if float(i['conf']) > 0.4:
    #                 print('识别green')
    #                 # return '识别green'
    #     # return '未识别信号灯'
    return {'light':x_result,'qr':y,'sign':z_result}

# @app.route('/test1',methods=['POST'])
# def qr_test():
#     res=img_send_model(request,read_qr,1)
#     return res

# @app.route('/test2',methods=['POST'])
# def light_test():
#     res=img_send_model(request,postprocess,1)
#     return res

def read_qr(frame):
    barcodes=pyzbar.decode(frame)
    data='None'
    for barcode in barcodes:
        #提取二维码数据
        data=barcode.data.decode('utf-8')
        # x,y,w,h=barcode.rect
        # data_type=barcode.type
        # cv2.rectangle(frame,(x,y),(x+w,y+h),[0,225,0],2)
        # cv2.putText(frame,data,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,[0,255,0],2)
        # print('data',data,'data_type',data_type)
    return data




# class showimg(threading.Thread):
#     def __init__(self):
#         super().__init__() #必须调用父类的初始化方法
#
#     def run(self) -> None:
#         while True:
#             cv2.imshow('img',img)
#             print(1)





#通过yolo预测图片中的目标
import time





#1加载模型
# model=YOLO('yolov8n.pt')

def postprocess(image):
    '''

    :param pred:  model 预测的结果
    :return:    解析之后的结果列表
    '''
    img = image
    pred = model(img)
    results =[]#初始化结果列表
    for res in pred:
        boxs = res.boxes
        for box in boxs:
            class_id=int(box.cls.cpu())
            bbox=box.xyxy[0].squeeze().tolist()
            result={
                'class_name':res.names[int(class_id)],
                'bbox':bbox,
                'class_id':class_id,
                'conf':box.conf[0].squeeze().tolist()
            }
            results.append(result)

    return results

def read_sign(image):
    '''

    :param pred:  model 预测的结果
    :return:    解析之后的结果列表
    '''
    img = image
    pred = model_sign(img)
    results =[]#初始化结果列表
    for res in pred:
        boxs = res.boxes
        for box in boxs:
            class_id=int(box.cls.cpu())
            bbox=box.xyxy[0].squeeze().tolist()
            result={
                'class_name':res.names[int(class_id)],
                'bbox':bbox,
                'class_id':class_id,
                'conf':box.conf[0].squeeze().tolist()
            }
            results.append(result)

    return results

# x1, y1, x2, y2 = box.xyxy[0]  # 获取检测框坐标
# conf = box.conf[0]  # 置信度
# c_id = box.cls[0]  # 类别id
# c_name = result.names[int(c_id)]  # 名字

#图片处理并调用对应的识别模型
# def img_send_model(img,model,select_model):
#     '''
#
#     :param img: 图片
#     :param model: 识别方法 二维码 yolo 其他
#     :select_model:yolo模型对象 红绿灯 交通标志 行人
#     :return:
#
#     '''
#
#     barcodes=pyzbar.decode(frame)
#     data='None'
#     for barcode in barcodes:
#         #提取二维码数据
#         data=barcode.data.decode('utf-8')
#         # x,y,w,h=barcode.rect
#         # data_type=barcode.type
#         # cv2.rectangle(frame,(x,y),(x+w,y+h),[0,225,0],2)
#         # cv2.putText(frame,data,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,[0,255,0],2)
#         # print('data',data,'data_type',data_type)
#
#     pass
#
# def yolo_main(img,model):
#     '''
#
#     :param img: 图片
#     :param model: 预加载之后的模型
#     :return: 预测结果
#     '''
#     pass
# def yolo(image):
#     # 4处理预测结果
#     img = image
#     results = model(img)
#
#     for result in results:
#         boxs = result.boxes
#         for box in boxs:
#             x1, y1, x2, y2 = box.xyxy[0].squeeze().tolist() # 获取检测框坐标
#             conf = box.conf[0]  # 置信度
#             c_id = box.cls[0]  # 类别id
#             c_name = result.names[int(c_id)]  # 名字
#
#             # print('name', c_name)
#             # print('conf', conf)
#             # print('c_id', c_id)
#             # print('xyxy', x1, y1, x2, y2)
#             cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
#             cv2.putText(img, f'{c_name}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 255, 0], 2)
#             cv2.putText(img, f'{conf}', (int(x1 + 30), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 255, 0], 2)
#






#将上述代码封装为方法
#测试树莓派小车通过摄像头发送给flask服务器识别 拿结果
#小车根据识别结果做相应的处理






if __name__=='__main__':
    # came = showimg()
    # came.start()
    app.run(host='0.0.0.0',port=8000,debug=True)
#hello_world

#练习 定义一个客户端能拿到摄像头的每一帧 发送给服务器作识别