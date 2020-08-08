# -*- coding: utf-8 -*-
"""YOLO_utils.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1di2vlUrwc-aOiPrHLvpz6iiNvsSRS9aa

This notebook consists of codes for basic processes that are going the assist the main YOLO funtion in notebook.
The processes are as follows:
1.Show image
2.Read Classes
3.Read anchors
4.Generate colours
5.Scale boxes
6.Pre-process image 
7.Draw boxes

**IMPORTING THE REQUIRED PACKAGES**

1.   colorsys is used to convert image from HSV coord to RGB coord
2.   imghdr Tests the image data contained in the file named by filename, and   returns a string describing the image type.
3.   os provides a portable way of using operating system dependent functionality
4.   random implements pseudo-random number generators for various distributions.
5.   numpy is used for working with arrays
6.   PIL is Python Imaging Library which enables opening, manipulating, and saving many different image file formats
"""

import colorsys
import imghdr
import os
import random
from keras import backend as K
import numpy as np
from PIL import Image, ImageDraw, ImageFont

"""**EXTRACT THE CLASS NAMES**

This model is trained using the MS-COCO dataset. This dataset has 80 object categories. The following cell is to extract each of the 80 classes. In the main YOLO code, the path of the coco classes file wil be passed to this function
"""

def read_classes(classes_path):
    with open(classes_path) as f:
        class_names = f.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names

"""**ANCHOR BOXES**

Generally, grid cells usually can make only prediction. But when it has to make more than one prediction, anchor boxes come into use. Anchor boxes are pre-defined boxes of different shapes. Anchor box which has the highest IoU with the object's shape is used. The following code will access the pre-defined anchors.
"""

def read_anchors(anchors_path):
    with open(anchors_path) as f:
        anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        anchors = np.array(anchors).reshape(-1, 2)
    return anchors

"""**GENERATE COLORS**

The following code cell is used to generate colors for the bounding boxes. It takes the class names as input which is returned by the read_classes function.
"""

def generate_colors(class_names):
    hsv_tuples = [(x / len(class_names), 1., 1.) for x in range(len(class_names))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))
    random.seed(10101)  # Fixed seed for consistent colors across runs.
    random.shuffle(colors)  # Shuffle colors to decorrelate adjacent classes.
    random.seed(None)  # Reset seed to default.
    return colors

"""**SCALE BOXES**

Scales the predicted boxes in order to be drawable on the image
"""

def scale_boxes(boxes, image_shape):
    height = image_shape[0]
    width = image_shape[1]
    image_dims = K.stack([height, width, height, width])
    image_dims = K.reshape(image_dims, [1, 4])
    boxes = boxes * image_dims
    return boxes

"""**PREPROCESS IMAGE**

This code provies the python interpreter the image editing capabilities and resizes it to the size that can be given as input to the YOLO model.
"""

def preprocess_image(img_path, model_image_size):
    image_type = imghdr.what(img_path)
    image = Image.open(img_path)
    resized_image = image.resize(tuple(reversed(model_image_size)), Image.BICUBIC)
    image_data = np.array(resized_image, dtype='float32')
    image_data /= 255.
    image_data = np.expand_dims(image_data, 0)  # Add batch dimension.
    return image, image_data

"""**DRAW BOXES**

This function is used to draw bounding boxes on the image file.
"""

def draw_boxes(image, out_scores, out_boxes, out_classes, class_names, colors):
    
    font = ImageFont.truetype(font='font/FiraMono-Medium.otf',size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
    thickness = (image.size[0] + image.size[1]) // 300

    for i, c in reversed(list(enumerate(out_classes))):
        predicted_class = class_names[c]
        box = out_boxes[i]
        score = out_scores[i]

        label = '{} {:.2f}'.format(predicted_class, score)

        draw = ImageDraw.Draw(image)
        label_size = draw.textsize(label, font)

        top, left, bottom, right = box
        top = max(0, np.floor(top + 0.5).astype('int32'))
        left = max(0, np.floor(left + 0.5).astype('int32'))
        bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
        right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
        print(label, (left, top), (right, bottom))

        if top - label_size[1] >= 0:
            text_origin = np.array([left, top - label_size[1]])
        else:
            text_origin = np.array([left, top + 1])

      
        for i in range(thickness):
            draw.rectangle([left + i, top + i, right - i, bottom - i], outline=colors[c])
        draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)], fill=colors[c])
        draw.text(text_origin, label, fill=(0, 0, 0), font=font)
        del draw