#!/bin/bash

# cd /home/$1
echo -e "Tarring logs ..."

PROJECT_PATH=$( dirname -- "$( readlink -f -- "$0"; )"; )
cd $PROJECT_PATH && cd  ..

for file in $(ls auto-review-archives/*.log 2> /dev/null)
do
    tar -czvf $(dirname $file)/$(basename $file).tar.gz -P $file
    rm -f $file
done

echo "Tarring OK"
