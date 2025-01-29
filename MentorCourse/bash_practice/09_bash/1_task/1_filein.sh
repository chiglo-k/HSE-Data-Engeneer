#! /bin/bash

echo "Write file: "

read file

echo "Write word: "

read word


grep -o -i "$word" "$file"|wc -l 
