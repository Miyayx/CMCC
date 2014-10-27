#!/bin/sh

path=`cat ../conf/path.properties`
path=${path:12}
val="${path}val/"
echo $val
others="${path}others/"
echo $others

mkdir $val
mkdir $others

python table_preprocess.py
#echo "DB output verify..."
#python db_validation.py > "${val}db.val"
echo "Feature verify..."
python table_validation.py > "${val}feature.val"
