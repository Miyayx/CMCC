#!/bin/sh

python classify_preprocess.py
echo "Feature verify..."
python new_validation.py > ../../data/Classify/val/feature.val
echo "Attribute verify..."
python attribute.py > ../../data/Classify/val/attr.val
