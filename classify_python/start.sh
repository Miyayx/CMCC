#!/bin/sh

DIR="../../data/Classify/"
val=${DIR}"val/"
others=${DIR}"others/"
mkdir $val
mkdir $others

python classify_preprocess.py
echo "DB output verify..."
python db_validation.py > ${val}db.val
echo "Feature verify..."
python feature_validation.py > ${val}feature.val
echo "Attribute verify..."
python attribute.py > ${val}attr.val
