#!/usr/bin/env python
#-*-coding:utf-8-*-

from validation import *

class SectionValidation(Validation):

    def run(self, props, Y):
    
        file_col = os.path.join(RESULT_PATH, props['file_col'])
        feature_file = os.path.join(RESULT_PATH, props['result_output']+'_'+'features'+str(Y)+'.csv')
        OTHERS_PATH = os.path.join(RESULT_PATH, props['others_output_path'])
    
        prop = read_properties(file_col) #get feature count from file_col file
    
    
        options = {
            "section":{
                "begin":2,
                "end":2+int(prop["section_count"]),
                "left_file":os.path.join(OTHERS_PATH, props['left_section_file']+'_features'+str(Y)+'.dat')
            },
            "block":{
                "begin":2+int(prop["section_count"]),
                "end":  2+int(prop["section_count"])+int(prop["block_count"]),
                "left_file":os.path.join(OTHERS_PATH, props['left_block_file']+'_features'+str(Y)+'.dat')
                },
            "table_header":{
                "begin":2+int(prop["section_count"])+int(prop["block_count"]),
                "end":  2+int(prop["section_count"])+int(prop["block_count"])+int(prop["table_header"]),
                "left_file":os.path.join(OTHERS_PATH, props['left_tableheader_file']+'_features'+str(Y)+'.dat')
                }
        }
        self.validation(feature_file,options)

if __name__=="__main__":
    props = read_properties(os.path.join(BASEDIR, PATH_FILE))
    props.update(read_properties(os.path.join(BASEDIR, FILE_FILE)))
    import sys
    Y = 1
    if len(sys.argv) == 2:
        Y = sys.argv[1]
    v = SectionValidation()
    v.run(props, Y)

