# -- coding: utf-8 --
import cv2

img = cv2.imread('seal.png')
img0 = img.copy()
b, g, r = cv2.split(img)
a = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, a = cv2.threshold(a, 240, 255, cv2.THRESH_BINARY)
a = cv2.bitwise_not(a, a)
img = cv2.merge((cv2.split(img), a))
cv2.imwrite("img.png", img)
