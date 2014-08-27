#!/bin/sh

python classify_preprocess.py
echo "DB output verify..."
python db_validation.py > ../../data/Classify/val/db.val
echo "Feature verify..."
python feature_validation.py > ../../data/Classify/val/feature.val
echo "Attribute verify..."
python attribute.py > ../../data/Classify/val/attr.val
