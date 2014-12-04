#!/bin/sh

path=`cat ../conf/path.properties`
path=${path:12}
val="${path}val/"
echo $val
others="${path}others/"
echo $others

mkdir $val
mkdir $others

python section_preprocess.py
echo "Feature verify..."
python section_validation.py > "${val}feature.val"
