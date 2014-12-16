#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
此文件为全局配置文件，记录各个配置文件的path
"""

import utils
import os

BASE_FILE="../../conf/conf.properties"
BASEDIR = utils.read_properties(BASE_FILE)['base.path']

DB_FILE="./conf/conf.properties"

PATH_FILE = "./conf/classify/path.properties"
PROP_FILE = "./conf/classify/classify.properties"
COL_FILE = "./conf/classify/file_col.properties"
NAME_FILE = "./conf/classify/filename.properties"
ANNOTATION_FILE = "./conf/classify/flag.cfg"
MULTI_ANNOTATION_FILE = "./conf/classify/multi_flag.cfg"
FILE_FILE="./conf/classify/file.cfg"
DOC_FEATURE_FILE="./conf/classify/feature.cfg"
SECTION_FEATURE_FILE="./conf/classify/sec_feature.cfg"
TABLE_FEATURE_FILE="./conf/classify/table_feature.cfg"

PATH_CONFIG = utils.read_properties(os.path.join(BASEDIR, PATH_FILE))

RESULT_PATH = os.path.join(BASEDIR, PATH_CONFIG['output_path'])#
LOG_PATH = os.path.join(BASEDIR, PATH_CONFIG['log_path'])

DEFAULT_RESULT_NAME = "result_features1.csv"
