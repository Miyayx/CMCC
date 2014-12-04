#/usr/env/python2.7
#encoding=utf-8

"""
和同义词相关的代码
"""

def get_synonym_words(fn):
    """
    """
    words = set()
    for line in open(fn):
        line = line.strip("\n").strip("\r").decode("utf-8")
        words.update(line.split(",")[:2])
    return list(words)

def get_synonym_dict(fn):
    """
    Returns:
        如果A，B，C是同义词，则他们最终都由同一个词，如A代替,这个替代的词A就是dict中的value
        dict (k:词, v:这个词的同义词)
    """
    d = {}# k:word, v: synonym word list(including k)
    l = []# list of synonym set
    word_syn = {}
    with open(fn) as f:
        line = f.readline().strip("\n").strip("\r").decode("utf-8")
        while line:
            ws = line.split(",")
            if int(ws[-1]) == 1:
                l.append(set(ws[:-1]))
            line = f.readline().strip("\n").strip("\r").decode("utf-8")

    print "synonym pair len:",len(l)

    i = 0
    while i < len(l):
        while True:
            j = 0
            length = len(l[i])
            while j < len(l):
                if len(l[i].intersection(l[j])) >  0:
                    l[i] = l[i].union(l[j])
                j += 1
            if length == len(l[i]):
                break
        i += 1

    for ws in l:
        k = min(ws)
        for w in ws:
            if w != k:
                word_syn[w] = k

    return word_syn, l

def expand_all_synonym(labels, syn_list):
    """
    Args:
        labels: list
        syn:    list of syn set
    Returns:
        A new list including all synonyms
    """
    new_l = set(labels)
    for s in syn_list:
        for i in s:
            new_l.add(i)
    return list(new_l)

def expand_use_synonym(labels, syn_list):
    """
    Args:
        labels: list
        syn:    list of syn set
    Returns:
        A new list including specific synonyms
    """
    new_l = set(labels)

    for l in labels:
        for s in syn_list:
            if l in s:
                for i in s:
                    new_l.add(i)

    return list(new_l)

def filter_use_synonym(labels, syn):
    """
    Args:
        labels: list
        syn:    dict
    Returns:
        A new list of labels without synonyms
    """
    new_l = set(labels)
    delete = set()
    add = set()
    for l in new_l:
        if syn.has_key(l):
            #print "Synonym:",l,syn[l]
            delete.add(l)
            add.add(syn[l])
    
    s = (new_l|add) - delete
    return list(s)

def filter_use_synonym2(labels, syn):
    """
    Args:
        labels: list
        syn:    dict
    Returns:
        A new list of labels without synonyms
    """
    new_l = set(labels)
    delete = set()
    add = set()
    for l in new_l:
        if syn.has_key(l):
            print "Synonym:",l,syn[l]
            delete.add(l)
            add.add(syn[l])

    return list((new_l|add)-delete)
