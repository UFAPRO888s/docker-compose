import requests
import os
import json
import uuid
import cv2
def draw_result(image,pred):
        image=image.copy()
        for i,(x,y,w,h,name,score) in enumerate(pred):
            box=[x,y,x+w,y+h]
            color = [225, 255, 255]
            thickness=2
            cv2.rectangle(image,(box[0],box[1]),(box[2],box[3]),color,int(thickness))
            cv2.putText(image,str(name),(box[0], box[1] - 2),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],int(thickness))
            cv2.putText(image,str(score),(box[0], box[1] - 5),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],int(thickness))
            cv2.putText(image,str(i),(box[0], box[1] - 8),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],int(thickness))
        return image
files = ['img1.jpeg', 'img2.jpeg']
url = 'http://localhost/api/yolo7/'
for x in files:
    print(x)
    file = {'file': open(x, 'rb')}
    r = requests.post(url, files=file)
    if r.ok:
        res = json.loads(r.text)
        print(res)
        img = cv2.imread(x)
        output=draw_result(img,res)
        filename = '/streaming/tmp/output.jpg'
        cv2.imwrite(filename, output)
    else:
        print('Fail to detect obj')