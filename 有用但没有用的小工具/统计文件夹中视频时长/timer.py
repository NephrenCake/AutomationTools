# -- coding: utf-8 --
import os
import cv2


def get_video_duration(filename):
    cap = cv2.VideoCapture(filename)
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        return duration
    return 0


def count_video_time(cur_path: str, lv: int = 0):
    text = "\t" * lv + "|-"
    tim = 0
    child_lines = []

    cur_dir = os.listdir(cur_path)
    if len(cur_dir) == 0:
        return "", tim

    for fn in cur_dir:
        child = cur_path + "/" + fn
        if os.path.isdir(child):
            child_line, child_time = count_video_time(child, lv + 1)
            child_lines.append(child_line)
            tim += child_time
        elif os.path.isfile(child) and fn.split(r".")[-1] in ["mp4"]:
            tim += get_video_duration(child)

    text += f"{cur_path} {round(tim / 3600, 2)} h"
    for child_line in child_lines:
        text += "\n" + child_line.split(cur_path)[0] + child_line.split(cur_path + "/")[-1]

    print(f"{cur_path}")
    return text, tim


root = r"G:\考研资料\2023\王道\习题课\04.组成原理"
res, t = count_video_time(root)
print(res)

with open(f"{root}/{round(t / 3600, 2)}.txt", mode="w", encoding="utf-8") as f:
    f.write(res)
    f.close()
