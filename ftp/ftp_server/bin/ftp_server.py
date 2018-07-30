import os,sys
#设置包路径
PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#添加包索引路径，用以查找main文件
sys.path.append(PATH)
from core import main

if __name__ == '__main__':
    main.ArgvHandler()
    print(PATH)