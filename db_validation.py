#/usr/bin/env python
#-*-coding:UTF-8-*-

from db import *

if __name__ == "__main__":
    db = DB()
    #调用db自己的验证过程进行section和block的验证
    db.section_validation()
    db.block_validation()
