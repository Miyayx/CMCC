
import codecs
with codecs.open("../etc/synonym_dict.csv", "w","utf-8") as fw:
    with open("../etc/labelled-data-1-s.txt") as fr:
        line = fr.readline().decode("utf-8")
        line = line[1:]
        while line:
            line = line.replace(";",",")
            fw.write(line)
            line = fr.readline().decode("utf-8")
