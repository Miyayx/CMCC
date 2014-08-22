#!/usr/bin/python2.7
#encoding=utf-8

class CSVIO:

    def __init__(self, fn, header=True, append=True):
        self.header = header
        self.append = append
        self.fields = []
        self.content = {}
        self.separator = ","
        self.columnN = 0
        self.rowN = 0
        if append:
            self.load(fn,header,",")

    def load(self, fn, header=True, separator=","):
        self.separator = separator
        self.header = header

        f = open(fn)
        if header:
            h = f.readline().strip("\n")
            self.fields = h.split(separator)

        maxColumnN = 0
        rowN = 0
        line = f.readline().strip("\n")
        while line:
            rowN += 1
            line = line.split(separator)
            self.content[line[0]] = line
            maxColumnN = len(line) if len(line) > maxColumnN else maxColumnN
            line = f.readline().strip("\n")

        self.columnN = maxColumnN
        self.rowN = rowN
            
        f.close()

    def column(self, colname, col):
        if colname in self.fields:
            self.update(self.fields.index(colname), col)
        elif(self.rowN == 0):
            print "first column",colname
            self.insert_column(colname, 0, col)
        else:
            print "add column",colname
            self.add_column(colname, col)

    def insert_column(self, colName, colindex, newCol):

        if not newCol or len(newCol) == 0 :
            print "Null Column Map"
            return 

        if self.header:
            if len(self.fields) == 0 or not self.fields:
                self.fields = []
            while len(self.fields) <= colindex:
                self.fields.append("")
            self.fields.insert(colindex, colName)

        keys = set()
        if self.append:
            keys.update(newCol.keys())
            keys.update(self.content.keys())
        else:
            if len(self.content) == 0:
                keys = newCol.keys()
            else:
                keys = set(self.content.keys()) & set(newCol.keys())

        for k in keys:
            if not self.content.has_key(k):
                value = []
            else: 
                value = self.content[k]
            while len(value) < colindex:
                value.append("")
            if newCol.has_key(k):
                value.insert(colindex, newCol[k])
            else:
                value.insert(colindex, "")
            self.content[k] = value

        self.columnN = len(self.content.values()[0])
        print "column",self.columnN
        print "fields len",len(self.fields)
        self.rowN = len(self.content)
        print "row",self.rowN

    def add_column(self, colname, col):
        self.insert_column(colname, self.columnN, col)

    def update_cell(self, key, col_index, new_s):
        """
        update one cell
        key: file name
        col_index: the column be updated
        new_s: new content
        """
        if not self.content.has_key(key):
            self.content[key] = [key]
        value = self.content[key]
        if col_index < len(value):
            value[col_index] = new_s
        else:
            value.append(new_s)
        self.content[key] = value

    def update(self, col_index, new_col):
        for k in self.content.keys():
            if(new_col.has_key(k)):
                self.update_cell(k, col_index, new_col[k])
            else:
                self.update_cell(k, col_index, " ")

    def write(self, fn, separator=',', header=True, sort=True, sort_index=0):
        """
        Write Content to file 
        """
        if sort:
       #     for v in self.content.values():
       #         print len(v)
            new_content = sorted(self.content.items(), key=lambda x: x[1][0])
            new_content = sorted(new_content, key=lambda x: x[1][sort_index])
            #sorted(self.content.items(), key=lambda x: x[1][sort_index], reverse=True)
        f = open(fn, 'w')
        if header:
            f.write(",".join(self.fields)+"\n")
        for k,v in new_content:
            f.write(",".join(v)+"\n")
            f.flush()
        f.close()

    def read_one_to_one(self, k_i, v_i):

        result = {}
        
        for con in self.content.values():
            result[con[k_i]] = con[v_i]

        return result
        
        
