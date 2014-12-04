#!/bin/sh

BASE=`grep '^base.path' ../../conf/conf.properties`
BASE=${BASE:12}
echo $BASE
path=`head -n 1 ../../conf/classify/path.properties`
path=$BASE${path:12}
echo $path
val="${path}val/"
echo $val
others="${path}others/"
echo $others

mkdir $path
mkdir $val
mkdir $others

python table_preprocess.py
echo "Feature verify..."
echo "Output in ${val}feature.val"
python table_validation.py > "${val}feature.val"
