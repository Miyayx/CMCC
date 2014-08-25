
#/usr/bin/python2.7
#-*-coding:UTF-8-*-

if __name__ == "__main__":
    db = DB('../../conf/conf.properties')
    db.section_validation()
    db.block_validation()
