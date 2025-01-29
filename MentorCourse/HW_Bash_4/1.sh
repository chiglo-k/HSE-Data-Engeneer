#!/bin/bash

# man test наше все

#1 Список файлов в директории, указывая их тип

for item in *; do
	if [ -d "$item" ]; then
		echo  "$item is a dir"
	elif [ -f "$item" ]; then
		echo "$item is a file"
	else
		echo "$item is another file"
	fi
done

#2 Проверка на наличие определенного файла

echo "Write you file: "

read name

if [ -z "$name" ]; then
	echo "$name this file doesnt exist"
else
	if [ -e "$name" ]; then
		echo "$name exist"
	else
		echo "Some kinda magik"
	fi
fi

#3 Информация о каждом файле

for file in *; do
	if [ -f "$file" ]; then
		permissions=$(ls -l "$file"| awk '{print $1}')
		echo "Name:$file, Permission:  $permissions"
	fi
done
