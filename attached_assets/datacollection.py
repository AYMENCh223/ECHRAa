import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
import os
from PIL import Image

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300
counter = 0

filename = "ب"
folder = "Data"
path = os.path.join(folder, filename)

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)*255

        imgCrop = img[y-offset:y + h + offset, x-offset:x + w + offset]
        imgCropShape = imgCrop.shape

        aspectRatio = h / w

        if aspectRatio > 1:
            k = imgSize / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize-wCal)/2)
            imgWhite[:, wGap: wCal + wGap] = imgResize

        else:
            k = imgSize / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize - hCal) / 2)
            imgWhite[hGap: hCal + hGap, :] = imgResize

        # cv2.imshow('ImageCrop', imgCrop)
        # cv2.imshow('ImageWhite', imgWhite)

    cv2.imshow('Image', img)
    key = cv2.waitKey(1)
    if key == ord("s"):
        if not os.path.exists(path):
            os.makedirs(path)
            print("file created")
        
        counter += 1
        # success = cv2.imwrite(os.path.join(path, f"Image_{time.time()}.jpg"), imgWhite)

        # cv2.imwrite(os.path.join(folder, arabic_reshaper.reshape(filename),f"Image_{time.time()}.jpg"), imgWhite)
        img_pil = Image.fromarray(imgWhite)
        img_pil.save(os.path.join(path, f"Image_{time.time()}.jpg"))
        print(os.path.join(path, f"Image_{time.time()}.jpg"))