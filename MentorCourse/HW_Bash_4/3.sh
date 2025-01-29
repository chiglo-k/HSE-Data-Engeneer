#!/bin/bash

#3 Проверка вводимого числа (+, -, 0) --> счет от 1 до введенного числа

echo "Give a number: " 
read number

if [ $number -eq 0 ];then
	echo "It's ZERO"
elif [ $number -gt 0 ]; then
	echo "It's positive number"
	counter=1
	while [ $counter -ne $number ]; do
		echo "$counter"
		((counter ++))
	done
else
	echo "$number less than zero"
fi
