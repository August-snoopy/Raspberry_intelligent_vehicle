import os
import torch
import yaml
from ultralytics import YOLO
from QtFusion.path import abs_path

# 选择是否GPU加速
device = '0' if torch.cuda.is_available() else 'cpu'

if __name__ == '__main__':
    works = 4 
    batch = 8
    data_path = abs_path(r'ultralytics-8.2.79\datasets\datasets\TrafficLight\TrafficLight.yaml', path_type = 'current')
    print(data_path)
    # 将路径更改为unix风格的路径    
    unix_data_path = data_path.replace(os.sep, '/')
    new_data_path = os.path.dirname(unix_data_path)
    # 读取数据集
    with open(data_path, 'r') as f:
        data = yaml.load(f, Loader = yaml.FullLoader)
    if 'path' in data:
        data['path'] = new_data_path
        # 将修改值写为新的yaml文件
        with open(data_path, 'w') as f:
            yaml.safe_dump(data, f, sort_keys = False)
    
    model = YOLO(abs_path(r'..\runs\detect\v8_TrafficLigtht\weights\best.pt'), task = 'detect')
    result = model.train(
        data = data_path, 
        imgsz = 64, 
        batch = batch, 
        workers = works, 
        device = device,  # 是否使用GPU加速
        epochs = 10,  # 训练次数
        name = 'v8_TrafficLigtht_1'
    )