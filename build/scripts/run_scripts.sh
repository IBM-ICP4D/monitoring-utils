#!/bin/bash


dir=$(pwd)
for py_file in $(find $dir -name *.py)
do
    echo "Running script "+$py_file
    python $py_file
done