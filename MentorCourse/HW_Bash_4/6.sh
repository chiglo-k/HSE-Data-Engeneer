#!/bin/bash

#6 Скрипт читает данные из предложенного файла (вместо  input.txt), подсчитывает строки, ошибки в error.log
set -e

echo "Write file, which you want to read: "
read file


read_file() {
    if [ -f "$file" ]; then
        cat "$file"
        count_words "$file"
    else
	none_file "$file"
    fi
}

count_words() {
    wc -l "$file" >> output.txt
}

none_file(){
   ls "$file" >> error.txt
}

read_file

