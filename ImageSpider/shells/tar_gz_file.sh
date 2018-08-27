#!/bin/sh
# 移动本目录下的图片到不同的子文件夹
BATCH_SIZE=10000
base_dir_name='part'
files=$(ls)
current_file_index=1
index=0
for file in ${files}; do
    index=$((index+`expr 1`))

    b=$(( $index % $BATCH_SIZE ))
    if [[ $b = 0 ]]; then
        echo $index
done