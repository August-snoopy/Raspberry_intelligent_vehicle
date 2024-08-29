import cv2

img = cv2.imread(r'D:\intelligent_car_project\641.jpg') 
cv2.line(img, (0, 0), (255, 255), (0, 0, 255), 5)
cv2.rectangle(img, (0, 0), (500, 500), (0, 255, 0), 10)
cv2.circle(img, (477, 63), 100, (255, 0, 0), 5)
cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# cap = cv2.VideoCapture(0)
# while True:
#     ret, frame = cap.read()
#     print(ret)
#     cv2.imshow('frame', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break