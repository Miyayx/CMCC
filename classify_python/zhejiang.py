# /usr/bin/python1.7
#encoding=utf-8

from bs4 import BeautifulSoup

def read_html(h):
    with open(h) as f:
        return BeautifulSoup(f.read())

def get_sections(h):
    import re

    sections = []
    soup = read_html(h)
    # from paragraph
    ps = soup.find_all("p")
    for p in ps:
        s = p.find("font")
        if s:
            s = s.find("span").text if s.find("span") else s.text
            if s.endswith(":") or s.endswith(u"："):
                s = ''.join((re.findall(ur"[\u4e00-\u9fa5]+",s)))#仅保留中文
                if len(s) > 10:
                    continue
                sections.append(s)

        #print p

    #from table
    ts = soup.find_all("table")
    for t in ts:
        tds = t.find("tr").find_all("td")
        for td in tds:
            s = td.text
            #if s.find("span"):
            #    s = s.find("span")
            #    if s.find("font"):
            #         s = s.find("font").text
            #elif s.find("font"):
            #    s = s.find("font")
            #    if s.find("span"):
            #        s = s.find("span").text
            #    elif s.find("a"):
            #        s = s.find("a").text
            
            s = ''.join((re.findall(ur"[\u4e00-\u9fa5]+",s)))
            if len(s) > 10:
                continue
            sections.append(s)
            
    return set(sections)

def get_htmls(path,l):
    import os
    items = os.listdir(path)
    for i in items:
        if path.endswith("/"):
            i = path + i
        else:
            i = (path+"/"+i)
        if os.path.isdir(i):
            get_htmls(i,l)
        elif i.endswith("htm") or i.endswith("html"):
            l.append(i)

def write(fn,d):
    import codecs
    with codecs.open(fn) as f:
        for k,v in d:
            s = ""
            s = (k+"\t")
            for label in v:
                s += (label+",")
            s = s[:-1]
            f.write(s+"\n")

def main():
    htmls = []
    get_htmls("/mnt/wind/tsinghua/CMCC/移动数据/资费套餐/浙江/",htmls)
    for h in htmls:
        d = {}
        d[h] = get_sections(h)
        print h
        print len(d[h])
        for s in d[h]:
            print s
        
if __name__=="__main__":
    main()
