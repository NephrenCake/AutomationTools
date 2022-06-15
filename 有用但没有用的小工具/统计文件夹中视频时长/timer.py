# -- coding: utf-8 --
import os
import subprocess
import re

import cv2


def get_length(filename):
    result = subprocess.Popen(["ffprobe", filename],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    for x in result.stdout.readlines():
        if b"Duration" in x:
            print(x)
            x = re.search(rb"Duration.+?\d{2}:(\d{2}):\d{2}", x)
            return int(x.group(1))


def get_video_duration(filename):
    cap = cv2.VideoCapture(filename)
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        return duration
    return -1


total = r"G:\考研资料\2022\03、2022数学\11、2022姜晓千\02.2022精讲班\2022线性代数基础课"
d_l = os.listdir(total)
d_t = []

for d in d_l:
    length = 0
    path = total + "/" + d
    ls = os.listdir(path)
    for l in ls:
        if l.endswith(".mp4"):
            f = path + "/" + l
            length += get_video_duration(f)
    t = round(length / 3600, 2)
    print(d, t, "h")
    d_t.append(t)

time = sum(d_t)
print(time, "h")

# x = 8.15 + 3.49 + 4.50 + 2.56 + 1.35 + 2.77 + 1.41 + 1.53 + 2.41 + 4.40 + 2.56
# print(x)
