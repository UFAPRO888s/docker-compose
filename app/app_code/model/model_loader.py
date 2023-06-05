import os
import cv2
import numpy as np
import random
import onnxruntime as ort
from collections import OrderedDict,namedtuple





class cached_property(object):
    """
    Descriptor (non-data) for building an attribute on-demand on first use.
    """

    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._attr_name = factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)

        # Cache the value; hide ourselves.
        setattr(instance, self._attr_name, attr)

        return attr


# Lables=get_labels(labelsPath)
# CFG=get_config(cfgpath)
# Weights=get_weights(wpath)
# nets=load_model(CFG,Weights)


class Yolo7:

    yolo_path = "./model/"
    labels_path = "coco.names"
    weights_path = "yolov7.onnx"
    cuda = False

    @cached_property
    def labels(self):
        # load the COCO class labels our YOLO model was trained on
        # labelsPath = os.path.sep.join([yolo_path, "yolo_v3/coco.names"])
        lpath = os.path.sep.join([self.yolo_path, self.labels_path])
        labels = open(lpath).read().strip().split("\n")
        return labels

    @cached_property
    def weights(self):
        # derive the paths to the YOLO weights and model configuration
        wpath = os.path.sep.join([self.yolo_path, self.weights_path])
        return wpath

    @cached_property
    def providers(self,cuda=cuda):
        if cuda:
            return ['CUDAExecutionProvider', 'CPUExecutionProvider']
        else:
            return ['CPUExecutionProvider']
    @cached_property
    def colors(self):
        return {name:[random.randint(0, 255) for _ in range(3)] for i,name in enumerate(self.labels)}
    @cached_property
    def session(self):
        return ort.InferenceSession(self.weights, providers=self.providers)
    def names(self):
        return self.labels
    def print_color_pair(self):
        print(zip(self.labels,self.colors))
    @cached_property
    def net(self):
        # load our YOLO object detector trained on COCO dataset (80 classes)
        print("[INFO] loading YOLO from disk...")
        net = cv2.dnn.readNetFromDarknet(self.config, self.weights)
        return net
    def letterbox(self,im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, r, (dw, dh)

    def get_predection(self, image):
        # img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.copy()
        ori_images = [image.copy()]
        image, ratio, dwdh = self.letterbox(image, auto=False)
        image = image.transpose((2, 0, 1))
        image = np.expand_dims(image, 0)
        image = np.ascontiguousarray(image)

        im = image.astype(np.float32)
        im /= 255
        outname = [i.name for i in self.session.get_outputs()]
        inname = [i.name for i in self.session.get_inputs()]
        inp = {inname[0]:im}
        # ONNX inference
        outputs = self.session.run(outname, inp)[0]
        # outputs
        # ori_images = [img.copy()]

        final_boxes = []
        for i,(batch_id,x0,y0,x1,y1,cls_id,score) in enumerate(outputs):
            image = ori_images[int(batch_id)]
            box = np.array([x0,y0,x1,y1])
            box -= np.array(dwdh*2)
            box /= ratio
            box = box.round().astype(np.int32)
            cls_id = int(cls_id)
            score = round(float(score),3)
            name = list(self.labels)[cls_id]
            (x, y) = box[:2].tolist()
            (w, h) = (box[2:]-box[:2]).tolist()
            final_boxes.append((x, y, w, h, str(name), score))
        return final_boxes

    def draw_result(self,image,pred):
        image=image.copy()
        for i,(x,y,w,h,name,score) in enumerate(pred):
            box=[x,y,x+w,y+h]
            color = self.colors[name]
            thickness=2
            cv2.rectangle(image,(box[0],box[1]),(box[2],box[3]),color,int(thickness))
            cv2.putText(image,str(name),(box[0], box[1] - 2),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],int(thickness))
            cv2.putText(image,str(score),(box[0], box[1] - 5),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],int(thickness))
            cv2.putText(image,str(i),(box[0], box[1] - 8),cv2.FONT_HERSHEY_SIMPLEX,0.75,[225, 255, 255],int(thickness))
        return image


