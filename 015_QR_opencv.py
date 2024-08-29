from pyzbar import pyzbar
import cv2

# 二维码数据处理的函数
def read_qr(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        # 提取二维码数据
        data = barcode.data.decode('utf-8')
        x, y, w, h = barcode.rect
        data_type = barcode.type
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, data, (x, y-10), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, (0, 255, 0))
        print('data', data, 'data_type', data_type)
    return frame

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
while ret:
    ret, frame = cap.read()
    frame = read_qr(frame)
    cv2.imshow('qrframe', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()