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

rm $path
rm $val
rm $others
mkdir $path
mkdir $val
mkdir $others

python classify_preprocess.py
echo "DB output verify..."
echo "Output in ${val}db.val"
python db_validation.py > "${val}db.val" 
echo "Feature verify..."
echo "Output in ${val}feature.val"
python feature_validation.py > "${val}feature.val"
echo "Attribute verify..."
echo "Output in ${val}attr.val"
python attribute.py > "${val}attr.val"
