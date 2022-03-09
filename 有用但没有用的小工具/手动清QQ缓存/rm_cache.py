# -- coding: utf-8 --
import os


def rm_cache(path):
    ls = os.listdir(path)
    for file in ls:
        file = os.path.join(path, file)
        if os.path.isdir(file):
            rm_cache(file)
        elif os.path.isfile(file):
            os.remove(file)
            print(f"remove: {file}")
        else:
            print(f"except: {file}")


uid = ""
root = rf"D:\Download\Cache\QQ\{uid}\Image"
rm_cache(root)
