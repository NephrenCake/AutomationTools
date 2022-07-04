# -- coding: utf-8 --
"""
@Author: NephrenCake
@Date: 2022/7/1
@Desc:
"""
import os


def find_file_by_name(cur_path: str, tar: str):
    res = []
    cur_dir = os.listdir(cur_path)
    if len(cur_dir) == 0:
        return res

    for fn in cur_dir:
        child = cur_path + "/" + fn

        if os.path.isdir(child):
            res += find_file_by_name(child, tar)
        elif os.path.isfile(child) and tar in fn:
            res.append(child)
            print(f"find {child}")
    return res


if __name__ == '__main__':
    result = find_file_by_name(r"G:\考研资料\2022\2022姜晓千\03.660", "587")
